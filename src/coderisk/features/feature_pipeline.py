"""Sklearn-compatible feature matrix builder."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from coderisk.features.diff_features import extract_diff_features
from coderisk.features.metadata_features import extract_metadata_features

FEATURE_ORDER: list[str] | None = None


def row_to_features(row: dict[str, Any] | pd.Series) -> dict[str, float]:
    data = dict(row)
    diff = extract_diff_features(
        str(data.get("diff_text", "")),
        files_changed=int(data.get("files_changed", 0) or 0),
    )
    meta = extract_metadata_features(data)
    # Prefer explicit churn if present
    if "file_churn" in data and data["file_churn"] is not None:
        diff["feat_file_churn"] = float(data["file_churn"])
    merged = {**diff, **meta}
    return merged


def build_feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    rows = [row_to_features(r) for r in df.to_dict(orient="records")]
    frame = pd.DataFrame(rows)
    global FEATURE_ORDER
    if FEATURE_ORDER is None:
        FEATURE_ORDER = sorted(frame.columns)
    return frame.reindex(columns=FEATURE_ORDER)


def make_preprocess_pipeline() -> Pipeline:
    """Impute + scale; fit only on training fold."""
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )


def fit_transform_features(
    train_df: pd.DataFrame,
    *other_dfs: pd.DataFrame,
) -> tuple[np.ndarray, list[np.ndarray], list[str], Pipeline]:
    """Fit preprocessing on train features only; transform others."""
    train_x = build_feature_frame(train_df)
    feature_names = list(train_x.columns)
    pipe = make_preprocess_pipeline()
    x_train = pipe.fit_transform(train_x)
    transformed = [pipe.transform(build_feature_frame(df).reindex(columns=feature_names)) for df in other_dfs]
    return x_train, transformed, feature_names, pipe


def save_feature_schema(path: Path | str, feature_names: list[str], meta: dict[str, Any] | None = None) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"feature_names": feature_names, "meta": meta or {}}
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def save_preprocess(path: Path | str, pipeline: Pipeline) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, path)
