"""Tests for synthetic demo dataset generation and validation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from coderisk.data.demo_dataset import (
    generate_demo_records,
    records_to_frame,
    validate_dataset,
    write_demo_dataset,
)


def test_generate_at_least_100_and_reproducible() -> None:
    a = generate_demo_records(120, seed=42)
    b = generate_demo_records(120, seed=42)
    assert len(a) >= 100
    assert [r.commit_sha for r in a] == [r.commit_sha for r in b]
    assert all(r.is_synthetic for r in a)
    assert all(r.label_source == "synthetic_demo" for r in a)


def test_validate_ok() -> None:
    df = records_to_frame(generate_demo_records(100, seed=7))
    report = validate_dataset(df)
    assert report["n_rows"] == 100
    assert report["n_positive"] + report["n_negative"] == 100
    assert 0 < report["positive_rate"] < 1


def test_validate_rejects_duplicate_sha() -> None:
    df = records_to_frame(generate_demo_records(20, seed=1))
    df.loc[1, "commit_sha"] = df.loc[0, "commit_sha"]
    with pytest.raises(ValueError, match="Duplicate"):
        validate_dataset(df)


def test_validate_rejects_empty_diff() -> None:
    df = records_to_frame(generate_demo_records(10, seed=2))
    df.loc[0, "diff_text"] = "   "
    with pytest.raises(ValueError, match="empty diff"):
        validate_dataset(df)


def test_write_demo_dataset(tmp_path: Path) -> None:
    path, report = write_demo_dataset(tmp_path, n_samples=100, seed=42)
    assert path.exists()
    loaded = pd.read_parquet(path)
    assert len(loaded) == 100
    assert report["is_synthetic"] is True
    assert (tmp_path / "README.md").exists()
