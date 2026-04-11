#!/usr/bin/env python3
"""Benchmark CodeRisk FastAPI latency and throughput.

Runs warm-up requests, then timed single and optional batch predicts.
Writes measured percentiles only — never invents latency numbers.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from coderisk.evaluation.latency import latency_percentiles, throughput_rps
from coderisk.logging_config import get_logger, setup_logging

logger = get_logger(__name__)

DEFAULT_PAYLOAD = {
    "diff_text": "diff --git a/app.py b/app.py\n@@ -1 +1 @@\n-print(0)\n+print(1)\n",
    "files_changed": 1,
    "lines_added": 1,
    "lines_deleted": 1,
    "author_tenure_days": 42,
}


def _rss_mb() -> float | None:
    try:
        import resource

        usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        # macOS reports bytes; Linux typically KiB
        if sys.platform == "darwin":
            return float(usage) / (1024.0 * 1024.0)
        return float(usage) / 1024.0
    except Exception:  # noqa: BLE001
        return None


def run_benchmark(
    *,
    base_url: str,
    n: int,
    warmup: int,
    timeout: float,
    batch_size: int,
) -> dict:
    base = base_url.rstrip("/")
    samples_ms: list[float] = []
    errors = 0

    with httpx.Client(base_url=base, timeout=timeout) as client:
        health = client.get("/health")
        health.raise_for_status()
        ready = client.get("/ready")
        ready.raise_for_status()
        if not ready.json().get("ready"):
            raise RuntimeError(f"API not ready: {ready.json()}")

        for _ in range(warmup):
            client.post("/predict", json=DEFAULT_PAYLOAD).raise_for_status()

        wall_start = time.perf_counter()
        for _ in range(n):
            t0 = time.perf_counter()
            try:
                resp = client.post("/predict", json=DEFAULT_PAYLOAD)
                resp.raise_for_status()
            except Exception:  # noqa: BLE001
                errors += 1
            else:
                samples_ms.append((time.perf_counter() - t0) * 1000.0)
        wall_elapsed = time.perf_counter() - wall_start

        batch_ms: list[float] = []
        if batch_size > 0:
            batch_body = {"items": [DEFAULT_PAYLOAD for _ in range(batch_size)]}
            for _ in range(max(10, n // 10)):
                t0 = time.perf_counter()
                resp = client.post("/predict/batch", json=batch_body)
                resp.raise_for_status()
                batch_ms.append((time.perf_counter() - t0) * 1000.0)

    if not samples_ms:
        raise RuntimeError("No successful timed requests; cannot report latency")

    report: dict = {
        "base_url": base,
        "n_requested": n,
        "n_success": len(samples_ms),
        "n_errors": errors,
        "warmup": warmup,
        "single": latency_percentiles(samples_ms),
        "throughput_rps": throughput_rps(len(samples_ms), wall_elapsed),
        "wall_seconds": wall_elapsed,
        "client_rss_mb": _rss_mb(),
        "sample_latencies_ms": samples_ms,
    }
    if batch_ms:
        report["batch"] = {
            "batch_size": batch_size,
            "n": len(batch_ms),
            **latency_percentiles(batch_ms),
        }
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Benchmark CodeRisk API")
    parser.add_argument("--base-url", default="http://127.0.0.1:8742")
    parser.add_argument("--n", type=int, default=100, help="Timed single requests (>=100 preferred)")
    parser.add_argument("--warmup", type=int, default=10)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument(
        "--output",
        default="reports/metrics/benchmark_api.json",
        help="Where to write measured results JSON",
    )
    args = parser.parse_args(argv)

    setup_logging()
    if args.n < 1:
        logger.error("n must be >= 1")
        return 2

    report = run_benchmark(
        base_url=args.base_url,
        n=args.n,
        warmup=args.warmup,
        timeout=args.timeout,
        batch_size=args.batch_size,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    # Persist raw samples for audit; summary stays measured-only.
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    summary = {
        "p50_ms": report["single"]["p50_ms"],
        "p95_ms": report["single"]["p95_ms"],
        "p99_ms": report["single"]["p99_ms"],
        "throughput_rps": report["throughput_rps"],
        "n_success": report["n_success"],
        "output": str(out),
    }
    print(json.dumps(summary, indent=2))
    logger.info(
        "benchmark_done p50=%.2f p95=%.2f rps=%.2f",
        summary["p50_ms"],
        summary["p95_ms"],
        summary["throughput_rps"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
