#!/usr/bin/env bash
# Quick smoke against a running CodeRisk API (no secrets).
set -euo pipefail
BASE_URL="${1:-http://127.0.0.1:8742}"

curl -fsS "$BASE_URL/health" | tee /dev/stderr | grep -q '"status":"ok"'
curl -fsS "$BASE_URL/ready" | tee /dev/stderr >/dev/null
curl -fsS -X POST "$BASE_URL/predict" \
  -H 'content-type: application/json' \
  -d '{"diff_text":"diff --git a/a.py b/a.py\n+print(1)\n","files_changed":1,"lines_added":1}' \
  | tee /dev/stderr | grep -q risk_score
echo "smoke_ok base_url=$BASE_URL"
