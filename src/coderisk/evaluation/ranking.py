"""Top-k ranking metrics for reviewer prioritization."""

from __future__ import annotations

import numpy as np


def precision_at_top_fraction(y_true: np.ndarray, y_score: np.ndarray, fraction: float = 0.1) -> float:
    y_true = np.asarray(y_true).astype(int)
    y_score = np.asarray(y_score).astype(float)
    n = len(y_true)
    k = max(1, int(round(n * fraction)))
    idx = np.argsort(-y_score)[:k]
    return float(y_true[idx].mean()) if k else 0.0


def recall_at_top_fraction(y_true: np.ndarray, y_score: np.ndarray, fraction: float = 0.1) -> float:
    y_true = np.asarray(y_true).astype(int)
    y_score = np.asarray(y_score).astype(float)
    total_pos = int(y_true.sum())
    if total_pos == 0:
        return 0.0
    n = len(y_true)
    k = max(1, int(round(n * fraction)))
    idx = np.argsort(-y_score)[:k]
    return float(y_true[idx].sum() / total_pos)
