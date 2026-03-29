# Model comparison (measured on synthetic demo)

| Metric | XGBoost | CodeBERT |
|---|---|---|
| `roc_auc` | 0.5851851851851851 | 0.9481481481481482 |
| `pr_auc` | 0.6021324354657689 | 0.8782627865961199 |
| `precision` | 0.5714285714285714 | 0.0 |
| `recall` | 0.4444444444444444 | 0.0 |
| `f1` | 0.5 | 0.0 |
| `precision_at_top_10pct` | 1.0 | 1.0 |
| `recall_at_top_10pct` | 0.2222222222222222 | 0.2222222222222222 |
| `brier` | 0.24945329878363154 | 0.23313859126959968 |

Latency and model size: NOT_MEASURED in this report.
