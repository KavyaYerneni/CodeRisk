"""Plot helpers for evaluation reports."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np
from sklearn.metrics import PrecisionRecallDisplay, RocCurveDisplay


def save_roc_pr_curves(y_true: np.ndarray, y_prob: np.ndarray, output_dir: Path | str) -> dict[str, str]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths: dict[str, str] = {}

    fig, ax = plt.subplots()
    RocCurveDisplay.from_predictions(y_true, y_prob, ax=ax)
    roc_path = out / "roc_curve.png"
    fig.savefig(roc_path, bbox_inches="tight")
    plt.close(fig)
    paths["roc_curve"] = str(roc_path)

    fig, ax = plt.subplots()
    PrecisionRecallDisplay.from_predictions(y_true, y_prob, ax=ax)
    pr_path = out / "pr_curve.png"
    fig.savefig(pr_path, bbox_inches="tight")
    plt.close(fig)
    paths["pr_curve"] = str(pr_path)
    return paths
