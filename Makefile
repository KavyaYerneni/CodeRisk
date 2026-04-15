.PHONY: install test lint typecheck health demo-data train-xgb train-codebert api benchmark docker-build docker-up

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

train-codebert:
	python scripts/train_codebert.py --config configs/demo.yaml

api:
	CODERISK_MODEL_DIR=$${CODERISK_MODEL_DIR:-artifacts/xgboost} \
		uvicorn coderisk.api.main:app --host 0.0.0.0 --port 8742

benchmark:
	python scripts/benchmark_api.py --base-url http://127.0.0.1:8742 --n 100

docker-build:
	docker build -t coderisk:local .

docker-up:
	docker compose up --build
