.PHONY: install test lint typecheck health demo-data train-xgb api benchmark

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest

lint:
	ruff check src tests scripts

typecheck:
	mypy src/coderisk

health:
	coderisk health

demo-data:
	python scripts/build_dataset.py --mode demo --output-dir data/processed/demo

train-xgb:
	python scripts/train_xgboost.py --config configs/demo.yaml

api:
	uvicorn coderisk.api.main:app --host 0.0.0.0 --port 8742

benchmark:
	python scripts/benchmark_api.py --base-url http://127.0.0.1:8742 --n 100
