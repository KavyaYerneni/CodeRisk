# Data card — CodeRisk

## Summary

CodeRisk currently ships a **synthetic demo dataset** for local development and tests. Optional GitHub mining is available behind explicit CLI flags and is not run by default.

## Demo dataset

| Field | Value |
|-------|-------|
| Path | `data/processed/demo/dataset.csv` |
| Rows | 120 (configurable) |
| Label source | `synthetic_demo` |
| `is_synthetic` | `true` for all rows |
| Seed | 42 (via `configs/demo.yaml`) |

### Record schema

`repository`, `pull_request_id`, `commit_sha`, `parent_sha`, `author`, `author_tenure_days`, `files_changed`, `lines_added`, `lines_deleted`, `file_churn`, `diff_text`, `bug_introducing_label` (0/1), `label_source`, `timestamp`, `is_synthetic`.

### Validation

`src/coderisk/data/demo_dataset.py` checks required columns, unique commit SHAs, binary labels, and reports class balance into `data/processed/demo/validation_report.json`.

## Mined / SZZ data (optional)

- Mining writes under `data/raw/` (gitignored).
- SZZ labels are heuristic; see `docs/szz_limitations.md`.
- Never present mined rows as ground-truth bug labels.

## Splits

Prefer `repository_time` for evaluation (documented in `docs/evaluation_splits.md`). Fit preprocessing on train only.

## Sensitive data

Do not commit tokens, private diffs, or large raw dumps. Use `GITHUB_TOKEN` from the environment only.
