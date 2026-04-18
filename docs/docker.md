# Docker

CPU-only FastAPI image. Model weights are **mounted**, not baked into the image.

## Build

```bash
# Train locally first so artifacts exist
python scripts/train_xgboost.py --config configs/demo.yaml

docker build -t coderisk:local .
# or
make docker-build
```

## Run with compose

```bash
docker compose up --build
# API: http://127.0.0.1:8742/health
```

Compose mounts `./artifacts/xgboost` read-only at `/models` (`CODERISK_MODEL_DIR`).

## Security notes

- Runs as non-root user `coderisk` (uid 10001).
- No secrets in the image; use env vars at runtime if needed.
- `.dockerignore` excludes `.venv`, raw data, and local artifacts.

## Health

Container healthcheck hits `GET /health`. `/ready` stays false until a valid model bundle is mounted.
