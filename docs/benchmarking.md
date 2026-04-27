# API benchmarking

Use `scripts/benchmark_api.py` against a running CodeRisk API to record **measured** latency.

## Prerequisites

1. Train or place an XGBoost bundle under `artifacts/xgboost` (gitignored).
2. Start the API: `make api` (or `uvicorn coderisk.api.main:app --port 8742`).
3. Confirm `GET /ready` reports `ready: true`.

## Run

```bash
python scripts/benchmark_api.py --base-url http://127.0.0.1:8742 --n 100
# or
make benchmark
```

Results write to `reports/metrics/benchmark_api.json` (raw sample latencies included). Do not quote latency in README or resume materials unless this file exists from a real run.

## Reported fields

- Single-request p50 / p95 / p99 (ms)
- Throughput (requests/sec over the timed window)
- Optional batch latency summary
- Client process RSS when available

## Checked-in example

A localhost run is saved at `reports/metrics/benchmark_api.md` (measured; not production latency).
