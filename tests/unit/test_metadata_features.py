from datetime import datetime, timezone

from coderisk.features.metadata_features import extract_metadata_features


def test_metadata_features() -> None:
    row = {
        "author_tenure_days": 40,
        "prior_commits": 3,
        "timestamp": datetime(2025, 1, 6, 15, 0, tzinfo=timezone.utc),  # Monday
    }
    feats = extract_metadata_features(row)
    assert feats["feat_author_tenure_days"] == 40.0
    assert feats["feat_hour_of_day"] == 15.0
    assert feats["feat_day_of_week"] == 0.0
