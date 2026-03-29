#!/usr/bin/env python3
"""Compare measured XGBoost and CodeBERT demo metrics on the same split recipe."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load(path: Path) -> dict:
    if not path.exists():
        return {"status": "NOT_MEASURED", "path": str(path)}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--xgb", default="reports/metrics/xgboost_demo.json")
    parser.add_argument("--codebert", default="reports/metrics/codebert_demo.json")
    parser.add_argument("--output", default="reports/metrics/model_comparison.json")
    args = parser.parse_args()

    xgb = _load(Path(args.xgb))
    cb = _load(Path(args.codebert))
    keys = [
        "roc_auc",
        "pr_auc",
        "precision",
        "recall",
        "f1",
        "precision_at_top_10pct",
        "recall_at_top_10pct",
        "brier",
    ]
    comparison = {
        "dataset": "synthetic_demo",
        "split_strategy": xgb.get("split", {}).get("strategy")
        or xgb.get("split_strategy")
        or cb.get("split_strategy")
        or "NOT_MEASURED",
        "models": {
            "xgboost": {k: xgb.get(k, "NOT_MEASURED") for k in keys},
            "codebert": {k: cb.get(k, "NOT_MEASURED") for k in keys},
        },
        "latency_ms": "NOT_MEASURED",
        "model_size": "NOT_MEASURED",
        "limitations": [
            "Metrics are from the synthetic demo dataset only.",
            "CodeBERT run used truncated max_train_samples for CPU demo training.",
            "Do not treat these numbers as resume claims for large-scale mined data.",
        ],
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(comparison, indent=2) + "\n", encoding="utf-8")
    md = out.with_suffix(".md")
    lines = [
        "# Model comparison (measured on synthetic demo)",
        "",
        "| Metric | XGBoost | CodeBERT |",
        "|---|---|---|",
    ]
    for k in keys:
        lines.append(
            f"| `{k}` | {comparison['models']['xgboost'][k]} | {comparison['models']['codebert'][k]} |"
        )
    lines.append("")
    lines.append("Latency and model size: NOT_MEASURED in this report.")
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
