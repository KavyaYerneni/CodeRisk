# Contributing

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

## Checks before a PR

```bash
ruff check src tests scripts
mypy src/coderisk
python -m pytest
```

## Commits

- Author: Kavya Yerneni <kavya.yerneni@sjsu.edu>
- Prefer small, focused commits with clear 1–2 line messages
- Do not commit secrets, raw mined dumps, or large model weights
- Do not invent metrics; only commit numbers from real runs

## Demo vs mining

Default workflows use synthetic demo data. Mining requires `GITHUB_TOKEN` and explicit CLI flags.
