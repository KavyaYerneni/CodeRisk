# Model card — CodeRisk

## Intended use

Score pull-request-like diffs for relative bug-introduction **risk** to help reviewers prioritize. Demo models are for methodology and local demos — not production gatekeeping.

## Models

### XGBoost baseline

- Features: diff + metadata via `coderisk.features.feature_pipeline`
- Training: `scripts/train_xgboost.py`
- Artifacts: `artifacts/xgboost/` (gitignored): `model.joblib`, `preprocess.joblib`, schemas, split IDs, metrics
- Measured demo metrics: `reports/metrics/xgboost_demo.json`

### CodeBERT (optional demo fine-tune)

- Input packing: `DIFF: … [SEP] FILES_CHANGED: …` (`coderisk.models.tokenizer`)
- CPU-compatible demo path with short epochs / sample caps
- Measured demo metrics: `reports/metrics/codebert_demo.json`
- ONNX export + parity: `scripts/export_onnx.py`, `reports/metrics/onnx_parity.json`

## Comparison

Same synthetic split where available: `reports/metrics/model_comparison.json`. Values are measured or marked `NOT_MEASURED`.

## Out of scope

- Guaranteeing a change is bug-free
- Replacing code review or tests
- Claiming large-scale (50k PR) performance without a measured run on that data

## Ethical considerations

Risk scores can bias review attention. Use as a triage signal with human oversight. Synthetic labels ≠ real defect history.
