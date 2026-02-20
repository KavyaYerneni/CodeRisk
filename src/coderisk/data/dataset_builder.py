"""Assemble train-ready tables from demo or mined sources."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from coderisk.data.demo_dataset import generate_demo_records, records_to_frame, validate_dataset
from coderisk.logging_config import get_logger

logger = get_logger(__name__)


def build_demo_frame(n_samples: int = 120, seed: int = 42, positive_rate: float = 0.35) -> pd.DataFrame:
    records = generate_demo_records(n_samples, seed=seed, positive_rate=positive_rate)
    df = records_to_frame(records)
    validate_dataset(df)
    return df


def load_processed_dataset(path: Path | str) -> pd.DataFrame:
    path = Path(path)
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    if path.suffix == ".csv":
        return pd.read_csv(path)
    raise ValueError(f"Unsupported dataset format: {path}")


def save_processed_dataset(df: pd.DataFrame, output_dir: Path | str) -> dict[str, Any]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "dataset.csv", index=False)
    try:
        df.to_parquet(out / "dataset.parquet", index=False)
    except Exception as exc:  # noqa: BLE001
        logger.warning("parquet_write_failed err=%s", exc)
    report = validate_dataset(df)
    return report
