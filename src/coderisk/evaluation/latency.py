"""Latency percentile helpers for API benchmarking."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np


def latency_percentiles(
    samples_ms: Iterable[float],
    percentiles: tuple[float, ...] = (50.0, 95.0, 99.0),
) -> dict[str, float]:
    """Compute latency percentiles from millisecond samples.

    Args:
        samples_ms: Observed request latencies in milliseconds.
        percentiles: Percentile points to compute (0–100).

    Returns:
        Mapping like ``{"p50_ms": ..., "p95_ms": ..., "p99_ms": ...}``.

    Raises:
        ValueError: If no samples are provided.
    """
    values = np.asarray(list(samples_ms), dtype=float)
    if values.size == 0:
        raise ValueError("samples_ms must be non-empty")
    out: dict[str, float] = {}
    for p in percentiles:
        key = f"p{int(p)}_ms" if float(p).is_integer() else f"p{p}_ms"
        out[key] = float(np.percentile(values, p))
    out["mean_ms"] = float(values.mean())
    out["n"] = float(values.size)
    return out


def throughput_rps(n_requests: int, elapsed_seconds: float) -> float:
    """Requests per second given count and wall time."""
    if elapsed_seconds <= 0:
        raise ValueError("elapsed_seconds must be positive")
    if n_requests < 0:
        raise ValueError("n_requests must be non-negative")
    return float(n_requests) / float(elapsed_seconds)
