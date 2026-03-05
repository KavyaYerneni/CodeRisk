"""Probability calibration utilities."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.isotonic import IsotonicRegression


def fit_isotonic(y_true: np.ndarray, y_prob: np.ndarray) -> IsotonicRegression:
    iso = IsotonicRegression(out_of_bounds="clip")
    iso.fit(y_prob, y_true)
    return iso


def apply_isotonic(iso: IsotonicRegression, y_prob: np.ndarray) -> np.ndarray:
    return iso.transform(y_prob)


def calibration_summary(y_true: np.ndarray, y_prob: np.ndarray, *, n_bins: int = 10) -> dict[str, Any]:
    """Simple reliability-style summary without fabricating claims."""
    y_true = np.asarray(y_true).astype(float)
    y_prob = np.asarray(y_prob).astype(float)
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    rows = []
    for i in range(n_bins):
        lo, hi = bins[i], bins[i + 1]
        mask = (y_prob >= lo) & (y_prob < hi if i < n_bins - 1 else y_prob <= hi)
        if not mask.any():
            continue
        rows.append(
            {
                "bin_left": float(lo),
                "bin_right": float(hi),
                "count": int(mask.sum()),
                "avg_pred": float(y_prob[mask].mean()),
                "avg_true": float(y_true[mask].mean()),
            }
        )
    return {"n_bins": n_bins, "bins": rows}
