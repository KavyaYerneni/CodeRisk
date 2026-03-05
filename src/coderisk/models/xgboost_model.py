"""XGBoost baseline trainer and persistence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from xgboost import XGBClassifier

from coderisk.logging_config import get_logger

logger = get_logger(__name__)


def compute_scale_pos_weight(y: np.ndarray) -> float:
    y = np.asarray(y).astype(int)
    n_pos = max(1, int((y == 1).sum()))
    n_neg = max(1, int((y == 0).sum()))
    return float(n_neg / n_pos)


def build_xgboost(params: dict[str, Any], *, scale_pos_weight: float, seed: int) -> XGBClassifier:
    cfg = {
        "n_estimators": int(params.get("n_estimators", 100)),
        "max_depth": int(params.get("max_depth", 4)),
        "learning_rate": float(params.get("learning_rate", 0.1)),
        "subsample": float(params.get("subsample", 0.9)),
        "colsample_bytree": float(params.get("colsample_bytree", 0.9)),
        "min_child_weight": float(params.get("min_child_weight", 1.0)),
        "reg_lambda": float(params.get("reg_lambda", 1.0)),
        "objective": "binary:logistic",
        "eval_metric": "logloss",
        "n_jobs": 2,
        "random_state": seed,
        "scale_pos_weight": scale_pos_weight,
    }
    return XGBClassifier(**cfg)


def train_xgboost(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_val: np.ndarray | None,
    y_val: np.ndarray | None,
    params: dict[str, Any],
    *,
    seed: int = 42,
) -> XGBClassifier:
    spw = params.get("scale_pos_weight")
    if spw is None:
        spw = compute_scale_pos_weight(y_train)
    model = build_xgboost(params, scale_pos_weight=float(spw), seed=seed)
    fit_kwargs: dict[str, Any] = {}
    if x_val is not None and y_val is not None:
        fit_kwargs["eval_set"] = [(x_val, y_val)]
        fit_kwargs["verbose"] = False
    model.fit(x_train, y_train, **fit_kwargs)
    logger.info("xgboost_trained n_train=%s scale_pos_weight=%s", len(y_train), spw)
    return model


def predict_proba(model: XGBClassifier, x: np.ndarray) -> np.ndarray:
    return model.predict_proba(x)[:, 1]


def save_xgboost_bundle(
    output_dir: Path | str,
    model: XGBClassifier,
    *,
    feature_names: list[str],
    preprocess_path: Path | str | None,
    config: dict[str, Any],
    metrics: dict[str, Any],
) -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    model_path = out / "model.joblib"
    joblib.dump(model, model_path)
    (out / "feature_names.json").write_text(json.dumps(feature_names, indent=2) + "\n", encoding="utf-8")
    (out / "config.json").write_text(json.dumps(config, indent=2, default=str) + "\n", encoding="utf-8")
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2, default=str) + "\n", encoding="utf-8")
    if preprocess_path is not None:
        (out / "preprocess_path.txt").write_text(str(preprocess_path) + "\n", encoding="utf-8")
    return model_path


def load_xgboost_model(model_dir: Path | str) -> tuple[XGBClassifier, list[str]]:
    model_dir = Path(model_dir)
    model = joblib.load(model_dir / "model.joblib")
    names = json.loads((model_dir / "feature_names.json").read_text(encoding="utf-8"))
    return model, names
