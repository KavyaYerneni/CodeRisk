"""Unit tests for latency percentile helpers."""

from __future__ import annotations

import pytest

from coderisk.evaluation.latency import latency_percentiles, throughput_rps


def test_latency_percentiles_basic() -> None:
    samples = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
    stats = latency_percentiles(samples)
    assert stats["n"] == 10.0
    assert stats["p50_ms"] == pytest.approx(55.0)
    assert stats["p95_ms"] == pytest.approx(95.5)
    assert stats["mean_ms"] == pytest.approx(55.0)


def test_latency_percentiles_rejects_empty() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        latency_percentiles([])


def test_throughput_rps() -> None:
    assert throughput_rps(100, 2.0) == pytest.approx(50.0)
    with pytest.raises(ValueError):
        throughput_rps(10, 0.0)
