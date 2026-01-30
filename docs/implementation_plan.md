# CodeRisk implementation plan

## Goal

Build an ML pull-request risk classifier that predicts whether a code change is likely to introduce a bug. Demo-first on synthetic data; optional GitHub mining behind explicit flags.

## Phases

| Phase | Focus | Exit criteria |
|-------|--------|---------------|
| 1 | Foundation | `pytest`, lint, config, health CLI |
| 2 | Demo dataset | ≥100 synthetic PRs, validation + tests |
| 3 | GitHub mining | Mocked client, CLI, cache/resume |
| 4 | SZZ labeling | Tiny git fixture tests, documented noise |
| 5 | Features | Diff + metadata pipeline, no leakage |
| 6 | Splits | Stratified / time / repo-grouped + leakage tests |
| 7 | XGBoost | Train on demo, measured metrics only |
| 8 | CodeBERT | CPU-compatible demo fine-tune path |
| 9 | Comparison | Same split; measured or `NOT_MEASURED` |
| 10 | ONNX | Export + ORT parity check |
| 11 | FastAPI | `/health`, `/ready`, `/predict` |
| 12 | Benchmark | p50/p95/p99 from real requests |
| 13 | Docker | CPU image + compose |
| 14 | Docs | README, cards, reproducibility report |

## Constraints

- No fabricated resume metrics.
- Secrets from env only; never committed.
- Author: Kavya Yerneni \<kavya.yerneni@sjsu.edu\>; commit dates 2026-01-29 … 2026-05-05.
- Tests after each phase before continuing.
