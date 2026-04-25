#!/usr/bin/env python3
"""Train the XGBoost baseline on the demo (or processed) dataset."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from coderisk.config import load_config
from coderisk.data.dataset_builder import build_demo_frame, load_processed_dataset
from coderisk.data.splits import make_splits, save_split_result
from coderisk.evaluation.metrics import binary_classification_metrics
from coderisk.evaluation.plots import save_roc_pr_curves
from coderisk.evaluation.ranking import precision_at_top_fraction, recall_at_top_fraction
from coderisk.evaluation.reports import write_json_report, write_markdown_report
from coderisk.features.feature_pipeline import (
    fit_transform_features,
    save_feature_schema,
    save_preprocess,
)
from coderisk.logging_config import get_logger, setup_logging
from coderisk.models.calibration import calibration_summary
from coderisk.models.xgboost_model import predict_proba, save_xgboost_bundle, train_xgboost


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Train XGBoost baseline")
    parser.add_argument("--config", default="configs/demo.yaml")
    parser.add_argument("--dataset", default=None, help="Optional CSV/Parquet path")
    parser.add_argument("--output-dir", default="artifacts/xgboost")
    args = parser.parse_args(argv)

    cfg = load_config(args.config)
    setup_logging(level=cfg.logging.level)
    logger = get_logger(__name__)

    if args.dataset:
        df = load_processed_dataset(args.dataset)
    else:
        ds = cfg.dataset
        df = build_demo_frame(
            int(ds.get("n_samples", 120)),
            seed=cfg.seed,
            positive_rate=float(ds.get("positive_rate", 0.35)),
        )

    split_cfg = cfg.split
    train, val, test, split_meta = make_splits(
        df,
        strategy=split_cfg.get("strategy", "repository_time"),
        test_size=float(split_cfg.get("test_size", 0.2)),
        val_size=float(split_cfg.get("val_size", 0.1)),
        seed=cfg.seed,
    )

    x_train, (x_val, x_test), feature_names, pipe = fit_transform_features(train, val, test)
    y_train = train["bug_introducing_label"].to_numpy()
    y_val = val["bug_introducing_label"].to_numpy()
    y_test = test["bug_introducing_label"].to_numpy()

    model = train_xgboost(x_train, y_train, x_val, y_val, cfg.xgboost, seed=cfg.seed)
    prob_test = predict_proba(model, x_test)
    metrics = binary_classification_metrics(y_test, prob_test)
    metrics["precision_at_top_10pct"] = precision_at_top_fraction(y_test, prob_test, 0.1)
    metrics["recall_at_top_10pct"] = recall_at_top_fraction(y_test, prob_test, 0.1)
    metrics["calibration"] = calibration_summary(y_test, prob_test)
    metrics["split"] = {
        "strategy": split_meta.strategy,
        "n_train": len(train),
        "n_val": len(val),
        "n_test": len(test),
        "class_balance": split_meta.class_balance,
    }
    metrics["n_features"] = len(feature_names)
    metrics["dataset"] = "synthetic_demo" if args.dataset is None else str(args.dataset)

    out = Path(args.output_dir)
    preprocess_path = out / "preprocess.joblib"
    save_preprocess(preprocess_path, pipe)
    save_feature_schema(out / "feature_schema.json", feature_names, {"seed": cfg.seed})
    save_split_result(out / "split_ids.json", split_meta)
    save_xgboost_bundle(
        out,
        model,
        feature_names=feature_names,
        preprocess_path=preprocess_path,
        config={"xgboost": cfg.xgboost, "seed": cfg.seed, "split": cfg.split},
        metrics=metrics,
    )
    fig_dir = Path(cfg.paths.reports) / "figures" / "xgboost"
    try:
        save_roc_pr_curves(y_test, prob_test, fig_dir)
    except Exception as exc:  # noqa: BLE001
        logger.warning("plot_failed err=%s", exc)

    write_json_report(Path(cfg.paths.reports) / "metrics" / "xgboost_demo.json", metrics)
    write_markdown_report(
        Path(cfg.paths.reports) / "metrics" / "xgboost_demo.md",
        "XGBoost demo metrics (measured)",
        {k: v for k, v in metrics.items() if k != "calibration"},
    )
    logger.info("xgboost_metrics %s", {k: metrics[k] for k in ("roc_auc", "pr_auc", "f1") if k in metrics})
    print(json_dumps_safe(metrics))
    return 0


def json_dumps_safe(metrics: dict) -> str:
    import json

    slim = {k: metrics[k] for k in ("roc_auc", "pr_auc", "f1", "precision_at_top_10pct", "recall_at_top_10pct", "n_features") if k in metrics}
    return json.dumps(slim)


if __name__ == "__main__":
    raise SystemExit(main())
