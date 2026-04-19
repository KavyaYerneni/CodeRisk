# Experiment tracking

Every training or evaluation run should leave an auditable footprint.

## Required artifacts per run

| Artifact | Purpose |
|----------|---------|
| Config YAML / `config.json` | Hyperparameters and paths |
| Random seed | Reproducibility |
| Split IDs (`split_ids.json`) | Leakage audits |
| Feature schema | Column contract |
| Preprocess pipeline | Train-only fit |
| Metrics JSON | Measured only |
| Model version / dir | Inference pin |

## Locations

- Configs: `configs/`
- Metrics reports: `reports/metrics/`
- Experiment scratch: `reports/experiments/` (gitignored contents)
- Model bundles: `artifacts/` (gitignored)

## Conventions

1. Do not overwrite metrics files without renaming if comparing runs — copy to `reports/experiments/<run_id>/` when iterating.
2. Record `dataset` field (`synthetic_demo` vs path to processed table).
3. Never invent AUC / latency / dataset size for docs or resume claims.

## Scripts that write metrics

- `scripts/train_xgboost.py` → `xgboost_demo.*`
- `scripts/train_codebert.py` → `codebert_demo.*`
- `scripts/compare_models.py` → `model_comparison.*`
- `scripts/export_onnx.py` → `onnx_parity.json`
- `scripts/benchmark_api.py` → `benchmark_api.*`
