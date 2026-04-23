# Resume claims — evidence status

Target claims from project context. Mark only after matching measured evidence exists.

| Claim | Status | Evidence |
|-------|--------|----------|
| 50k+ PRs / 200+ repos with SZZ labels | **UNSUPPORTED** | Demo is synthetic 120 rows; mining is optional |
| CodeBERT AUC 0.84 on large-scale data | **UNSUPPORTED** | Demo CodeBERT metrics only (`codebert_demo.json`) |
| +6pp precision@top-10% vs XGBoost at scale | **UNSUPPORTED** | Comparison file is synthetic-demo only |
| FastAPI + ONNX p95 ~85ms CPU (prod-like) | **UNSUPPORTED** | Localhost XGBoost API p95 ≈ 1.07 ms (`benchmark_api.md`); not ONNX/prod network |
| Open-source dataset, weights, training | **PARTIAL** | Code + demo data + train scripts open; weights gitignored (rebuildable) |

Update this table only when new measured reports are committed.
