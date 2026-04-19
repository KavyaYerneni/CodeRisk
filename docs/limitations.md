# Limitations

## Labels

- Synthetic demo labels are generated for pipeline testing, not real bugs.
- SZZ is noisy (keyword fix detection, blame ambiguity, renames). See `docs/szz_limitations.md`.

## Evaluation

- Demo metrics use 120 synthetic rows; absolute AUC values will move on real data.
- Repository-time splits reduce leakage but shrink per-repo test sets.
- Ranking metrics (P@top10%) are unstable on tiny test folds.

## Models

- XGBoost ignores raw token semantics beyond engineered features.
- CodeBERT demo fine-tunes are short / truncated; treat as a wiring proof, not SOTA.
- ONNX parity is checked on the exported demo model only.

## Serving

- Localhost benchmark latency is not cross-network or production latency.
- API returns 503 when artifacts are missing (safe startup), which can look like failures in misconfigured deploys.

## Operations

- Large-scale mining needs `GITHUB_TOKEN`, disk, and rate-limit patience; default mode stays demo-sized.
- Docker image is CPU-oriented; GPU paths are optional and undocumented as default.
