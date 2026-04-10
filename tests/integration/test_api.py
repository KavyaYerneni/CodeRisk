"""API integration tests using FastAPI TestClient."""

from __future__ import annotations

from fastapi.testclient import TestClient

from coderisk.api.dependencies import init_predictor
from coderisk.api.main import app


def test_health_ready_predict() -> None:
    init_predictor("artifacts/xgboost")
    with TestClient(app) as client:
        h = client.get("/health")
        assert h.status_code == 200
        assert h.json()["status"] == "ok"

        r = client.get("/ready")
        assert r.status_code == 200
        assert r.json()["ready"] is True

        info = client.get("/model-info")
        assert info.status_code == 200
        assert "features" in info.json()

        pred = client.post(
            "/predict",
            json={
                "diff_text": "diff --git a/a.py b/a.py\n+print(1)\n",
                "files_changed": 1,
                "lines_added": 1,
                "lines_deleted": 0,
                "author_tenure_days": 10,
            },
        )
        assert pred.status_code == 200
        body = pred.json()
        assert 0.0 <= body["risk_score"] <= 1.0

        batch = client.post(
            "/predict/batch",
            json={"items": [{"diff_text": "+x\n"}, {"diff_text": "+y\n"}]},
        )
        assert batch.status_code == 200
        assert len(batch.json()["results"]) == 2


def test_predict_rejects_huge_diff() -> None:
    init_predictor("artifacts/xgboost")
    with TestClient(app) as client:
        resp = client.post("/predict", json={"diff_text": "x" * 60_000})
        assert resp.status_code == 413
