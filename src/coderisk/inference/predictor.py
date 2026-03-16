"""Unified predictor for XGBoost (and optional CodeBERT) bundles."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from coderisk.features.feature_pipeline import build_feature_frame, row_to_features
from coderisk.models.xgboost_model import load_xgboost_model, predict_proba
from coderisk.schemas import PredictRequest, PredictResponse


class RiskPredictor:
    def __init__(self, model_dir: Path | str) -> None:
        self.model_dir = Path(model_dir)
        self.model = None
        self.feature_names: list[str] = []
        self.preprocess = None
        self.model_name = "xgboost"
        self.model_version = "0.1.0"
        self._load()

    def _load(self) -> None:
        if not (self.model_dir / "model.joblib").exists():
            return
        self.model, self.feature_names = load_xgboost_model(self.model_dir)
        preprocess_path = self.model_dir / "preprocess.joblib"
        if preprocess_path.exists():
            self.preprocess = joblib.load(preprocess_path)
        meta_path = self.model_dir / "config.json"
        if meta_path.exists():
            import json

            cfg = json.loads(meta_path.read_text(encoding="utf-8"))
            self.model_version = str(cfg.get("seed", self.model_version))

    @property
    def ready(self) -> bool:
        return self.model is not None and self.preprocess is not None

    def predict_one(self, req: PredictRequest) -> PredictResponse:
        if not self.ready:
            raise RuntimeError("Model not loaded")
        row = req.model_dump()
        frame = pd.DataFrame([row_to_features(row)])
        frame = frame.reindex(columns=self.feature_names, fill_value=0.0)
        x = self.preprocess.transform(frame)
        score = float(predict_proba(self.model, x)[0])
        return PredictResponse(
            risk_score=score,
            model_name=self.model_name,
            model_version=str(self.model_version),
            calibrated=False,
        )

    def predict_many(self, reqs: list[PredictRequest]) -> list[PredictResponse]:
        return [self.predict_one(r) for r in reqs]
