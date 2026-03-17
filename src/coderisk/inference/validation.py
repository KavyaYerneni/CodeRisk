"""Request validation helpers for inference."""

from __future__ import annotations

from coderisk.schemas import PredictRequest


class DiffTooLargeError(ValueError):
    pass


def validate_predict_request(req: PredictRequest, *, max_diff_chars: int = 50_000) -> PredictRequest:
    if req.diff_text is None or not str(req.diff_text).strip():
        raise ValueError("diff_text is required")
    if len(req.diff_text) > max_diff_chars:
        raise DiffTooLargeError(f"diff_text exceeds max_diff_chars={max_diff_chars}")
    if req.files_changed < 0 or req.lines_added < 0 or req.lines_deleted < 0:
        raise ValueError("change counts must be non-negative")
    return req
