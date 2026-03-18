"""Export CodeBERT sequence classifier to ONNX and validate ORT parity."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from coderisk.logging_config import get_logger

logger = get_logger(__name__)


def export_codebert_onnx(
    model_dir: Path | str,
    output_path: Path | str,
    *,
    max_length: int = 256,
    opset: int = 14,
) -> Path:
    model_dir = Path(model_dir)
    if not model_dir.exists():
        raise FileNotFoundError(f"CodeBERT model missing: {model_dir}")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)
    model.eval()

    dummy = tokenizer(
        "DIFF: example [SEP] FILES_CHANGED: 1",
        return_tensors="pt",
        padding="max_length",
        truncation=True,
        max_length=max_length,
    )
    input_names = ["input_ids", "attention_mask"]
    dynamic_axes = {
        "input_ids": {0: "batch", 1: "sequence"},
        "attention_mask": {0: "batch", 1: "sequence"},
        "logits": {0: "batch"},
    }
    if "token_type_ids" in dummy:
        input_names.append("token_type_ids")
        dynamic_axes["token_type_ids"] = {0: "batch", 1: "sequence"}

    args = tuple(dummy[name] for name in input_names)
    torch.onnx.export(
        model,
        args if len(args) > 1 else args[0],
        str(output_path),
        input_names=input_names,
        output_names=["logits"],
        dynamic_axes=dynamic_axes,
        opset_version=opset,
    )
    logger.info("exported_onnx path=%s", output_path)
    return output_path


def validate_onnx_parity(
    model_dir: Path | str,
    onnx_path: Path | str,
    *,
    max_length: int = 256,
    rtol: float = 1e-3,
    atol: float = 1e-4,
) -> dict[str, Any]:
    import onnxruntime as ort

    model_dir = Path(model_dir)
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)
    model.eval()
    text = "DIFF: parity check [SEP] FILES_CHANGED: 2"
    enc = tokenizer(text, return_tensors="pt", padding="max_length", truncation=True, max_length=max_length)
    with torch.no_grad():
        torch_logits = model(**enc).logits.numpy()

    session = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
    ort_inputs = {k: v.numpy() for k, v in enc.items() if k in {i.name for i in session.get_inputs()}}
    ort_logits = session.run(None, ort_inputs)[0]
    max_abs = float(np.max(np.abs(torch_logits - ort_logits)))
    ok = bool(np.allclose(torch_logits, ort_logits, rtol=rtol, atol=atol))
    return {"ok": ok, "max_abs_diff": max_abs, "torch_logits": torch_logits.tolist(), "ort_logits": ort_logits.tolist()}
