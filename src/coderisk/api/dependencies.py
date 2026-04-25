"""FastAPI dependencies and shared application state."""

from __future__ import annotations

from dataclasses import dataclass, field

from coderisk.config import get_env_settings
from coderisk.inference.predictor import RiskPredictor


@dataclass
class AppState:
    predictor: RiskPredictor | None = None
    model_dir: str = field(default_factory=lambda: get_env_settings().coderisk_model_dir)
    max_diff_chars: int = 50_000
    load_error: str | None = None


STATE = AppState()


def get_state() -> AppState:
    return STATE


def init_predictor(model_dir: str | None = None) -> AppState:
    settings = get_env_settings()
    STATE.model_dir = model_dir or settings.coderisk_model_dir
    try:
        STATE.predictor = RiskPredictor(STATE.model_dir)
        if not STATE.predictor.ready:
            STATE.load_error = f"Model artifacts missing in {STATE.model_dir}"
        else:
            STATE.load_error = None
    except Exception as exc:  # noqa: BLE001
        STATE.predictor = None
        STATE.load_error = str(exc)
    return STATE
