"""Tests for configuration loading."""

from __future__ import annotations

from pathlib import Path

import pytest

from coderisk.config import load_config


def test_load_demo_config() -> None:
    cfg = load_config("configs/demo.yaml")
    assert cfg.seed == 42
    assert cfg.mode == "demo"
    assert cfg.dataset["n_samples"] >= 100
    assert cfg.paths.data_processed == "data/processed"


def test_missing_config_raises(tmp_path: Path) -> None:
    missing = tmp_path / "nope.yaml"
    with pytest.raises(FileNotFoundError):
        load_config(missing)


def test_base_only_defaults() -> None:
    cfg = load_config()
    assert cfg.project_name == "coderisk"
    assert cfg.seed == 42
