"""Shared Pydantic schemas for records and API payloads."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class PullRequestRecord(BaseModel):
    """Canonical PR-like training record."""

    repository: str
    pull_request_id: int
    commit_sha: str
    parent_sha: str
    author: str
    author_tenure_days: float = Field(ge=0)
    files_changed: int = Field(ge=0)
    lines_added: int = Field(ge=0)
    lines_deleted: int = Field(ge=0)
    file_churn: float = Field(ge=0)
    diff_text: str
    bug_introducing_label: Literal[0, 1]
    label_source: str
    timestamp: datetime
    is_synthetic: bool = True

    @field_validator("commit_sha", "parent_sha")
    @classmethod
    def _non_empty_sha(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("SHA must be non-empty")
        return value.strip()


class PredictRequest(BaseModel):
    """Single prediction request."""

    repository: str = "unknown/repo"
    pull_request_id: int = 0
    author: str = "unknown"
    author_tenure_days: float = 30.0
    files_changed: int = 1
    lines_added: int = 1
    lines_deleted: int = 0
    file_churn: float = 1.0
    diff_text: str
    timestamp: datetime | None = None


class PredictResponse(BaseModel):
    """Risk score response."""

    risk_score: float = Field(ge=0.0, le=1.0)
    model_name: str
    model_version: str
    calibrated: bool = False


class BatchPredictRequest(BaseModel):
    items: list[PredictRequest] = Field(min_length=1, max_length=64)


class BatchPredictResponse(BaseModel):
    results: list[PredictResponse]


class HealthResponse(BaseModel):
    status: str
    version: str


class ReadyResponse(BaseModel):
    ready: bool
    model_loaded: bool
    detail: str | None = None


class ModelInfoResponse(BaseModel):
    model_name: str
    model_version: str
    model_dir: str
    features: list[str] | None = None
