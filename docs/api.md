# HTTP API

Base URL default: `http://127.0.0.1:8742`

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness; always OK if process is up |
| GET | `/ready` | True when model bundle loaded |
| GET | `/model-info` | Model name, version, feature list (503 if unloaded) |
| POST | `/predict` | Single risk score |
| POST | `/predict/batch` | Up to 64 items |

OpenAPI: `/docs` (Swagger UI) when the app is running.

## Predict body (JSON)

```json
{
  "diff_text": "diff --git a/x.py b/x.py\n+print(1)\n",
  "files_changed": 1,
  "lines_added": 1,
  "lines_deleted": 0,
  "author_tenure_days": 30,
  "repository": "acme/app",
  "pull_request_id": 1,
  "author": "dev"
}
```

Oversized diffs return **413** (see `max_diff_chars`, default 50_000). Missing model returns **503**.

## Env

| Variable | Default |
|----------|---------|
| `CODERISK_MODEL_DIR` | `artifacts/xgboost` |
| `CODERISK_LOG_LEVEL` | `INFO` |
| `CODERISK_HOST` / `CODERISK_PORT` | used by operators; uvicorn flags also work |
