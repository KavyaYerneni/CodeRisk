"""CodeBERT fine-tuning for PR risk (CPU-compatible demo path)."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup

from coderisk.logging_config import get_logger
from coderisk.models.tokenizer import build_codebert_text

logger = get_logger(__name__)


class PrTextDataset(Dataset):
    def __init__(self, texts: list[str], labels: list[int], tokenizer, max_length: int) -> None:
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.texts)

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        enc = self.tokenizer(
            self.texts[idx],
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt",
        )
        item = {k: v.squeeze(0) for k, v in enc.items()}
        item["labels"] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item


@dataclass
class CodeBertTrainResult:
    model_dir: str
    epochs_trained: int
    max_length: int
    n_train: int
    n_val: int
    device: str
    train_loss_last: float | None


def _class_weights(y: np.ndarray) -> torch.Tensor:
    n_pos = max(1, int((y == 1).sum()))
    n_neg = max(1, int((y == 0).sum()))
    # weight for [class0, class1]
    w0 = len(y) / (2.0 * n_neg)
    w1 = len(y) / (2.0 * n_pos)
    return torch.tensor([w0, w1], dtype=torch.float)


def train_codebert(
    train_rows: list[dict[str, Any]],
    val_rows: list[dict[str, Any]],
    *,
    output_dir: Path | str,
    model_name: str = "microsoft/codebert-base",
    max_length: int = 256,
    epochs: int = 1,
    batch_size: int = 4,
    grad_accum: int = 2,
    learning_rate: float = 2e-5,
    seed: int = 42,
    max_train_samples: int | None = 64,
) -> CodeBertTrainResult:
    torch.manual_seed(seed)
    np.random.seed(seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if max_train_samples is not None:
        train_rows = train_rows[: max_train_samples]
        val_rows = val_rows[: max(8, max_train_samples // 4)]

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
    model.to(device)

    train_texts = [build_codebert_text(r) for r in train_rows]
    val_texts = [build_codebert_text(r) for r in val_rows]
    y_train = np.array([int(r["bug_introducing_label"]) for r in train_rows])
    y_val = [int(r["bug_introducing_label"]) for r in val_rows]

    train_ds = PrTextDataset(train_texts, y_train.tolist(), tokenizer, max_length)
    val_ds = PrTextDataset(val_texts, y_val, tokenizer, max_length)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size)

    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
    total_steps = max(1, (len(train_loader) * epochs) // max(1, grad_accum))
    scheduler = get_linear_schedule_with_warmup(optimizer, 0, total_steps)
    weights = _class_weights(y_train).to(device)
    loss_fn = torch.nn.CrossEntropyLoss(weight=weights)

    last_loss: float | None = None
    model.train()
    for epoch in range(epochs):
        running = 0.0
        optimizer.zero_grad()
        for step, batch in enumerate(train_loader, start=1):
            batch = {k: v.to(device) for k, v in batch.items()}
            labels = batch.pop("labels")
            outputs = model(**batch)
            loss = loss_fn(outputs.logits, labels) / grad_accum
            loss.backward()
            if step % grad_accum == 0 or step == len(train_loader):
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()
            running += float(loss.item()) * grad_accum
        last_loss = running / max(1, len(train_loader))
        logger.info("codebert_epoch=%s train_loss=%s", epoch + 1, last_loss)

        # early-ish stop signal: evaluate val loss; keep training for demo epochs
        model.eval()
        with torch.no_grad():
            val_losses = []
            for batch in val_loader:
                batch = {k: v.to(device) for k, v in batch.items()}
                labels = batch.pop("labels")
                outputs = model(**batch)
                val_losses.append(float(loss_fn(outputs.logits, labels).item()))
            logger.info("codebert_val_loss=%s", float(np.mean(val_losses)) if val_losses else None)
        model.train()

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(out)
    tokenizer.save_pretrained(out)
    result = CodeBertTrainResult(
        model_dir=str(out),
        epochs_trained=epochs,
        max_length=max_length,
        n_train=len(train_rows),
        n_val=len(val_rows),
        device=str(device),
        train_loss_last=last_loss,
    )
    (out / "train_result.json").write_text(json.dumps(asdict(result), indent=2) + "\n", encoding="utf-8")
    return result


def predict_codebert_proba(model_dir: Path | str, texts: list[str], *, max_length: int = 256, batch_size: int = 8) -> np.ndarray:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)
    model.to(device)
    model.eval()
    probs: list[float] = []
    with torch.no_grad():
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i : i + batch_size]
            enc = tokenizer(
                batch_texts,
                truncation=True,
                padding=True,
                max_length=max_length,
                return_tensors="pt",
            )
            enc = {k: v.to(device) for k, v in enc.items()}
            logits = model(**enc).logits
            p = torch.softmax(logits, dim=-1)[:, 1].detach().cpu().numpy()
            probs.extend(float(x) for x in p)
    return np.asarray(probs, dtype=float)
