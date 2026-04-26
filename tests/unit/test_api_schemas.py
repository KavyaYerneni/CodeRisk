"""Schema validation tests for API payloads."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from coderisk.schemas import BatchPredictRequest, PredictRequest, PredictResponse


def test_predict_request_requires_diff() -> None:
    with pytest.raises(ValidationError):
        PredictRequest()  # type: ignore[call-arg]


def test_predict_response_bounds() -> None:
    ok = PredictResponse(risk_score=0.5, model_name="xgboost", model_version="42")
    assert ok.risk_score == 0.5
    with pytest.raises(ValidationError):
        PredictResponse(risk_score=1.5, model_name="x", model_version="1")


def test_batch_bounds() -> None:
    with pytest.raises(ValidationError):
        BatchPredictRequest(items=[])
    item = PredictRequest(diff_text="+x\n")
    batch = BatchPredictRequest(items=[item])
    assert len(batch.items) == 1
