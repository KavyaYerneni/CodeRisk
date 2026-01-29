# CodeRisk

CodeRisk is an ML-powered pull request risk classifier. It scores PRs for merge risk from code-change signals so reviewers can prioritize what needs the most attention.

## Get started

```bash
# Install dependencies (when the project layout lands)
pip install -e .

# Train or evaluate the classifier
python -m coderisk train
python -m coderisk predict --pr <number>
```

See upcoming docs in this repo for dataset layout, features, and model artifacts.
