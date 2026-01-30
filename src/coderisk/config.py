"""YAML + environment configuration loading."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PathConfig(BaseModel):
    data_raw: str = "data/raw"
    data_interim: str = "data/interim"
    data_processed: str = "data/processed"
    artifacts: str = "artifacts"
    reports: str = "reports"


class LoggingConfig(BaseModel):
    level: str = "INFO"
    json_logs: bool = False


class AppConfig(BaseModel):
    seed: int = 42
    project_name: str = "coderisk"
    mode: str = "demo"
    paths: PathConfig = Field(default_factory=PathConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    dataset: dict[str, Any] = Field(default_factory=dict)
    split: dict[str, Any] = Field(default_factory=dict)
    xgboost: dict[str, Any] = Field(default_factory=dict)
    codebert: dict[str, Any] = Field(default_factory=dict)
    api: dict[str, Any] = Field(default_factory=dict)


class EnvSettings(BaseSettings):
    """Secrets and runtime overrides from the environment."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    github_token: str | None = Field(default=None, alias="GITHUB_TOKEN")
    coderisk_host: str = Field(default="0.0.0.0", alias="CODERISK_HOST")
    coderisk_port: int = Field(default=8742, alias="CODERISK_PORT")
    coderisk_model_dir: str = Field(default="artifacts/xgboost", alias="CODERISK_MODEL_DIR")
    coderisk_log_level: str = Field(default="INFO", alias="CODERISK_LOG_LEVEL")


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, value in override.items():
        if key in out and isinstance(out[key], dict) and isinstance(value, dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def load_yaml(path: Path | str) -> dict[str, Any]:
    """Load a YAML file into a dict."""
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Config root must be a mapping: {path}")
    return data


def load_config(
    config_path: Path | str | None = None,
    *,
    base_path: Path | str = "configs/base.yaml",
) -> AppConfig:
    """Load base config, optional overlay, and apply env log level."""
    merged: dict[str, Any] = {}
    base = Path(base_path)
    if base.exists():
        merged = load_yaml(base)
    if config_path is not None:
        overlay = Path(config_path)
        if not overlay.exists():
            raise FileNotFoundError(f"Config not found: {overlay}")
        merged = _deep_merge(merged, load_yaml(overlay))

    env = EnvSettings()
    logging_cfg = merged.setdefault("logging", {})
    if isinstance(logging_cfg, dict) and "CODERISK_LOG_LEVEL" in os.environ:
        logging_cfg["level"] = env.coderisk_log_level

    return AppConfig.model_validate(merged)


def get_env_settings() -> EnvSettings:
    """Return environment-backed settings."""
    return EnvSettings()
