# Reproducibility report

## Environment (local demo)

- Python 3.11
- Install: `pip install -e ".[dev]"`
- Seed: `42` (`configs/demo.yaml`)

## Commands that reproduce measured demo artifacts

```bash
python scripts/build_dataset.py --mode demo --output-dir data/processed/demo
python scripts/train_xgboost.py --config configs/demo.yaml
# Optional / slower:
# python scripts/train_codebert.py --config configs/demo.yaml
# python scripts/export_onnx.py --model-dir artifacts/codebert
python scripts/compare_models.py
CODERISK_MODEL_DIR=artifacts/xgboost uvicorn coderisk.api.main:app --port 8742
python scripts/benchmark_api.py --base-url http://127.0.0.1:8742 --n 100
python -m pytest
```

## Measured outputs checked into git

| File | What it records |
|------|-----------------|
| `reports/metrics/xgboost_demo.json` | XGBoost on synthetic demo |
| `reports/metrics/codebert_demo.json` | CodeBERT demo fine-tune |
| `reports/metrics/model_comparison.json` | Side-by-side measured metrics |
| `reports/metrics/onnx_parity.json` | ONNX vs PyTorch check |
| `reports/metrics/benchmark_api.json` | Localhost API latency |

Model weight files under `artifacts/` are **not** committed; regenerate with the train scripts.

## What is not claimed

- 50k PRs / 200 repos (mining supported, not defaulted)
- Production cross-host p95 ≈ 85 ms (localhost demo p95 is in `benchmark_api.md`)
- CodeBERT AUC 0.84 as a large-scale result (demo JSON only)
