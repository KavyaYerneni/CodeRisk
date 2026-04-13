# Measured API benchmark (localhost)

Source: `scripts/benchmark_api.py` against `http://127.0.0.1:8742` with XGBoost artifacts.

| Metric | Value |
|--------|-------|
| n_success | 100 |
| n_errors | 0 |
| warmup | 10 |
| p50_ms | 0.995 |
| p95_ms | 1.072 |
| p99_ms | 1.107 |
| mean_ms | 1.003 |
| throughput_rps | 996.43 |
| wall_seconds | 0.1004 |
| client_rss_mb | 45.0 |

Batch (size 8):

| Metric | Value |
|--------|-------|
| p50_ms | 4.789 |
| p95_ms | 5.011 |

Notes:
- These figures are **localhost** CPU inference for the demo XGBoost bundle.
- Do not treat them as production or cross-host latency claims.
- Raw samples: `reports/metrics/benchmark_api.json`.
