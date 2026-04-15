"""Smoke tests for benchmark CLI argument parsing (no network)."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

import pytest

from coderisk.evaluation.latency import latency_percentiles, throughput_rps


def test_benchmark_main_rejects_zero_n(capsys) -> None:
    script = Path("scripts/benchmark_api.py")
    sys.argv = [str(script), "--n", "0", "--output", "reports/metrics/benchmark_api.json"]
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(script), run_name="__main__")
    assert exc.value.code == 2


def test_latency_helpers_available() -> None:
    assert latency_percentiles([1.0, 2.0, 3.0])["n"] == 3.0
    assert throughput_rps(10, 2.0) == 5.0
