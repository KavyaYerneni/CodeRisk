# CodeRisk

CodeRisk is an ML pull-request risk classifier: it scores whether a code change is likely to introduce a bug so reviewers can prioritize attention.

**Demo-first.** Synthetic data is labeled `synthetic_demo`. Metrics in this repo are **measured local runs only** — never fabricated resume numbers.

## Quick start

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
coderisk health
python -m pytest
```

## Demo dataset

```bash
python scripts/build_dataset.py --mode demo --output-dir data/processed/demo
```

120 synthetic PR-like rows with validation report under `data/processed/demo/`.

## Train XGBoost (baseline)

```bash
python scripts/train_xgboost.py --config configs/demo.yaml
# writes artifacts/xgboost/ and updates reports/metrics/xgboost_demo.*
```

## Optional CodeBERT demo fine-tune

```bash
python scripts/train_codebert.py --config configs/demo.yaml
python scripts/export_onnx.py --model-dir artifacts/codebert
python scripts/compare_models.py
```

## API

```bash
CODERISK_MODEL_DIR=artifacts/xgboost uvicorn coderisk.api.main:app --host 0.0.0.0 --port 8742
# GET /health /ready /model-info
# POST /predict  /predict/batch
```

## Benchmark (measured localhost)

```bash
python scripts/benchmark_api.py --base-url http://127.0.0.1:8742 --n 100
```

See `reports/metrics/benchmark_api.md` for the checked-in localhost run.

## Docker

```bash
python scripts/train_xgboost.py --config configs/demo.yaml
docker compose up --build
```

Details: `docs/docker.md`.

## Mining (optional)

```bash
export GITHUB_TOKEN=...   # never commit
python scripts/mine_repositories.py --repo owner/name --dry-run
python scripts/mine_repositories.py --repo owner/name --limit 20 --output-dir data/raw
```

## Docs

| Doc | Topic |
|-----|-------|
| `docs/implementation_plan.md` | Phased plan |
| `docs/architecture.md` | System diagram |
| `docs/data_card.md` / `docs/model_card.md` | Data & models |
| `docs/experiment_tracking.md` | Run artifacts |
| `docs/limitations.md` / `docs/ethics.md` | Caveats |
| `docs/szz_limitations.md` | SZZ noise |
| `docs/evaluation_splits.md` | Split strategy |
| `docs/benchmarking.md` / `docs/docker.md` | Serve & measure |
| `reports/reproducibility_report.md` | How to re-run |
| `reports/resume_claims.md` | Claim vs evidence |

## Measured demo snapshot (synthetic only)

From committed reports (re-run to refresh):

- XGBoost ROC-AUC / PR-AUC: see `reports/metrics/xgboost_demo.json`
- CodeBERT demo metrics: `reports/metrics/codebert_demo.json`
- Comparison: `reports/metrics/model_comparison.json`
- Localhost API p95: `reports/metrics/benchmark_api.md`

Large-scale resume targets remain **unsupported** until mined-data experiments are measured (`reports/resume_claims.md`).

## License

MIT — see `LICENSE`.
