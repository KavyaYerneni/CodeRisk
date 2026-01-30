# CodeRisk

CodeRisk is an ML-powered pull request risk classifier. It scores PRs for merge risk from code-change signals so reviewers can prioritize what needs the most attention.

## Status

Demo-first project. Synthetic demo data is clearly labeled. Metrics in docs are only those measured from local runs—never fabricated resume numbers.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
coderisk health
python -m pytest
```

See `docs/implementation_plan.md` for the phased build plan. Full usage (training, API, Docker) is documented as each phase lands.

## License

MIT — see `LICENSE`.
