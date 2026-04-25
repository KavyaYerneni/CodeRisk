#!/usr/bin/env python3
"""Evaluate a saved XGBoost bundle on a dataset split."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import joblib

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from coderisk.data.dataset_builder import build_demo_frame, load_processed_dataset
from coderisk.data.splits import make_splits
from coderisk.evaluation.metrics import binary_classification_metrics
from coderisk.evaluation.ranking import precision_at_top_fraction, recall_at_top_fraction
from coderisk.features.feature_pipeline import build_feature_frame
from coderisk.logging_config import setup_logging
from coderisk.models.xgboost_model import load_xgboost_model, predict_proba


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate saved models")
    parser.add_argument("--model-dir", default="artifacts/xgboost")
    parser.add_argument("--dataset", default=None)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args(argv)
    setup_logging()

    if args.dataset:
        df = load_processed_dataset(args.dataset)
    else:
        df = build_demo_frame(120, seed=args.seed)

    _, _, test, _ = make_splits(df, strategy="repository_time", seed=args.seed)
    model, feature_names = load_xgboost_model(args.model_dir)
    pipe = joblib.load(Path(args.model_dir) / "preprocess.joblib")
    x = pipe.transform(build_feature_frame(test).reindex(columns=feature_names, fill_value=0))
    y = test["bug_introducing_label"].to_numpy()
    prob = predict_proba(model, x)
    metrics = binary_classification_metrics(y, prob)
    metrics["precision_at_top_10pct"] = precision_at_top_fraction(y, prob, 0.1)
    metrics["recall_at_top_10pct"] = recall_at_top_fraction(y, prob, 0.1)
    print(json.dumps(metrics, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
