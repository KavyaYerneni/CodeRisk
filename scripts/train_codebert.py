#!/usr/bin/env python3
"""Fine-tune CodeBERT on the demo dataset (CPU-friendly defaults)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from coderisk.config import load_config
from coderisk.data.dataset_builder import build_demo_frame
from coderisk.data.splits import make_splits
from coderisk.evaluation.metrics import binary_classification_metrics
from coderisk.evaluation.ranking import precision_at_top_fraction, recall_at_top_fraction
from coderisk.evaluation.reports import write_json_report, write_markdown_report
from coderisk.logging_config import get_logger, setup_logging
from coderisk.models.codebert_model import predict_codebert_proba, train_codebert
from coderisk.models.tokenizer import build_codebert_text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Train CodeBERT demo model")
    parser.add_argument("--config", default="configs/demo.yaml")
    parser.add_argument("--output-dir", default="artifacts/codebert")
    parser.add_argument("--skip-download-smoke", action="store_true", help="Unused; reserved")
    args = parser.parse_args(argv)

    cfg = load_config(args.config)
    setup_logging(level=cfg.logging.level)
    logger = get_logger(__name__)

    df = build_demo_frame(
        int(cfg.dataset.get("n_samples", 120)),
        seed=cfg.seed,
        positive_rate=float(cfg.dataset.get("positive_rate", 0.35)),
    )
    train, val, test, split_meta = make_splits(
        df,
        strategy=cfg.split.get("strategy", "repository_time"),
        test_size=float(cfg.split.get("test_size", 0.2)),
        val_size=float(cfg.split.get("val_size", 0.1)),
        seed=cfg.seed,
    )
    cb = cfg.codebert
    result = train_codebert(
        train.to_dict(orient="records"),
        val.to_dict(orient="records"),
        output_dir=args.output_dir,
        model_name=str(cb.get("model_name", "microsoft/codebert-base")),
        max_length=int(cb.get("max_length", 256)),
        epochs=int(cb.get("epochs", 1)),
        batch_size=int(cb.get("batch_size", 4)),
        grad_accum=int(cb.get("grad_accum", 2)),
        learning_rate=float(cb.get("learning_rate", 2e-5)),
        seed=cfg.seed,
        max_train_samples=cb.get("max_train_samples", 64),
    )

    test_rows = test.to_dict(orient="records")
    texts = [build_codebert_text(r) for r in test_rows]
    y_test = test["bug_introducing_label"].to_numpy()
    probs = predict_codebert_proba(args.output_dir, texts, max_length=int(cb.get("max_length", 256)))
    metrics = binary_classification_metrics(y_test, probs)
    metrics["precision_at_top_10pct"] = precision_at_top_fraction(y_test, probs, 0.1)
    metrics["recall_at_top_10pct"] = recall_at_top_fraction(y_test, probs, 0.1)
    metrics["train_result"] = result.__dict__
    metrics["split_strategy"] = split_meta.strategy
    metrics["dataset"] = "synthetic_demo"
    metrics["note"] = "Measured on synthetic demo with truncated CodeBERT fine-tune; not a production claim."

    write_json_report(Path(cfg.paths.reports) / "metrics" / "codebert_demo.json", metrics)
    write_markdown_report(
        Path(cfg.paths.reports) / "metrics" / "codebert_demo.md",
        "CodeBERT demo metrics (measured)",
        {k: v for k, v in metrics.items() if k not in {"train_result"}},
    )
    logger.info("codebert_metrics roc_auc=%s pr_auc=%s", metrics.get("roc_auc"), metrics.get("pr_auc"))
    print(json.dumps({k: metrics.get(k) for k in ("roc_auc", "pr_auc", "f1", "precision_at_top_10pct")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
