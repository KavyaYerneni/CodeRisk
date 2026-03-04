import numpy as np

from coderisk.evaluation.metrics import binary_classification_metrics
from coderisk.evaluation.ranking import precision_at_top_fraction, recall_at_top_fraction


def test_metrics_and_ranking() -> None:
    y_true = np.array([0, 0, 1, 1, 1, 0, 1, 0])
    y_prob = np.array([0.1, 0.2, 0.9, 0.8, 0.7, 0.4, 0.6, 0.3])
    m = binary_classification_metrics(y_true, y_prob)
    assert m["roc_auc"] is not None
    assert 0.0 <= m["f1"] <= 1.0
    p = precision_at_top_fraction(y_true, y_prob, 0.25)
    r = recall_at_top_fraction(y_true, y_prob, 0.25)
    assert 0.0 <= p <= 1.0
    assert 0.0 <= r <= 1.0
