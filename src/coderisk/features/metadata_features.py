"""Author and repository metadata features (no future leakage)."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any


def extract_metadata_features(row: Mapping[str, Any]) -> dict[str, float]:
    """Extract metadata features available at prediction time.

    Does not use post-merge outcomes. Prior-history counts must be supplied
    by the caller from past-only aggregates.
    """
    ts = row.get("timestamp")
    if isinstance(ts, str):
        ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    hour = float(ts.hour) if isinstance(ts, datetime) else -1.0
    dow = float(ts.weekday()) if isinstance(ts, datetime) else -1.0
    return {
        "feat_author_tenure_days": float(row.get("author_tenure_days", 0.0) or 0.0),
        "feat_prior_commits": float(row.get("prior_commits", 0.0) or 0.0),
        "feat_prior_prs": float(row.get("prior_prs", 0.0) or 0.0),
        "feat_prior_bug_introducing": float(row.get("prior_bug_introducing", 0.0) or 0.0),
        "feat_repo_activity_30d": float(row.get("repo_activity_30d", 0.0) or 0.0),
        "feat_hours_since_prev_commit": float(row.get("hours_since_prev_commit", -1.0) or -1.0),
        "feat_reviewers": float(row.get("reviewers", 0.0) or 0.0),
        "feat_hour_of_day": hour,
        "feat_day_of_week": dow,
    }
