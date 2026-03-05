import numpy as np

from coderisk.models.xgboost_model import compute_scale_pos_weight, predict_proba, train_xgboost


def test_train_xgboost_smoke() -> None:
    rng = np.random.default_rng(0)
    x = rng.normal(size=(80, 5))
    y = (x[:, 0] + rng.normal(scale=0.5, size=80) > 0).astype(int)
    model = train_xgboost(x, y, x[:20], y[:20], {"n_estimators": 20, "max_depth": 2}, seed=0)
    prob = predict_proba(model, x[:10])
    assert prob.shape == (10,)
    assert compute_scale_pos_weight(y) > 0
