"""HTTP routes for CodeRisk API."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from coderisk import __version__
from coderisk.api.dependencies import get_state
from coderisk.inference.validation import DiffTooLargeError, validate_predict_request
from coderisk.schemas import (
    BatchPredictRequest,
    BatchPredictResponse,
    HealthResponse,
    ModelInfoResponse,
    PredictRequest,
    PredictResponse,
    ReadyResponse,
)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version=__version__)


@router.get("/ready", response_model=ReadyResponse)
def ready() -> ReadyResponse:
    state = get_state()
    loaded = bool(state.predictor and state.predictor.ready)
    return ReadyResponse(
        ready=loaded,
        model_loaded=loaded,
        detail=None if loaded else (state.load_error or "model not loaded"),
    )


@router.get("/model-info", response_model=ModelInfoResponse)
def model_info() -> ModelInfoResponse:
    state = get_state()
    if not state.predictor or not state.predictor.ready:
        raise HTTPException(status_code=503, detail=state.load_error or "model not loaded")
    return ModelInfoResponse(
        model_name=state.predictor.model_name,
        model_version=str(state.predictor.model_version),
        model_dir=state.model_dir,
        features=list(state.predictor.feature_names),
    )


@router.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest) -> PredictResponse:
    state = get_state()
    if not state.predictor or not state.predictor.ready:
        raise HTTPException(status_code=503, detail=state.load_error or "model not loaded")
    try:
        validate_predict_request(req, max_diff_chars=state.max_diff_chars)
    except DiffTooLargeError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return state.predictor.predict_one(req)


@router.post("/predict/batch", response_model=BatchPredictResponse)
def predict_batch(req: BatchPredictRequest) -> BatchPredictResponse:
    state = get_state()
    if not state.predictor or not state.predictor.ready:
        raise HTTPException(status_code=503, detail=state.load_error or "model not loaded")
    results = []
    for item in req.items:
        try:
            validate_predict_request(item, max_diff_chars=state.max_diff_chars)
        except DiffTooLargeError as exc:
            raise HTTPException(status_code=413, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        results.append(state.predictor.predict_one(item))
    return BatchPredictResponse(results=results)
