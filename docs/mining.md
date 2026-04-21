# GitHub mining

Optional pipeline for downloading PR metadata. **Not** run by default.

## Auth

```bash
export GITHUB_TOKEN=ghp_...   # or fine-grained token with repo read
```

Never commit tokens. `.env` is gitignored; see `.env.example`.

## CLI

```bash
python scripts/mine_repositories.py --repo owner/name --dry-run
python scripts/mine_repositories.py --repo owner/name --limit 50 --output-dir data/raw --resume
```

Supports allow/deny filters, JSONL cache, rate-limit retries, and pagination. Unit tests mock the network.

## Outputs

Raw JSONL/Parquet under `data/raw/` (gitignored). Build labeled tables separately via SZZ (`scripts/run_szz.py`) and `scripts/build_dataset.py`.
