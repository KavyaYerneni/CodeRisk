"""Deterministic synthetic demo dataset for local development."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

from coderisk.logging_config import get_logger
from coderisk.schemas import PullRequestRecord

logger = get_logger(__name__)

REQUIRED_COLUMNS = [
    "repository",
    "pull_request_id",
    "commit_sha",
    "parent_sha",
    "author",
    "author_tenure_days",
    "files_changed",
    "lines_added",
    "lines_deleted",
    "file_churn",
    "diff_text",
    "bug_introducing_label",
    "label_source",
    "timestamp",
    "is_synthetic",
]

REPOS = [
    "demo/payments-service",
    "demo/inventory-api",
    "demo/auth-gateway",
    "demo/billing-worker",
    "demo/search-indexer",
]

AUTHORS = ["alice", "bob", "carol", "dave", "erin", "frank"]


def _sha(seed: str) -> str:
    return hashlib.sha1(seed.encode("utf-8")).hexdigest()


def _diff_text(i: int, files: int, added: int, deleted: int, risky: bool) -> str:
    marker = "FIXME risky null deref" if risky else "refactor helper"
    hunks = []
    for f in range(max(1, files)):
        path = f"src/module_{i % 7}/file_{f}.py"
        hunks.append(
            f"diff --git a/{path} b/{path}\n"
            f"--- a/{path}\n+++ b/{path}\n"
            f"@@ -1,3 +1,{3 + added // max(files, 1)} @@\n"
            f" def fn_{f}():\n"
            f"-    return {deleted}\n"
            f"+    # {marker}\n"
            f"+    return {added + f}\n"
        )
    return "".join(hunks)


def generate_demo_records(
    n_samples: int = 120,
    *,
    seed: int = 42,
    positive_rate: float = 0.35,
) -> list[PullRequestRecord]:
    """Generate deterministic synthetic PR-like records.

    Labels and diffs are synthetic (`label_source=synthetic_demo`).
    """
    if n_samples < 1:
        raise ValueError("n_samples must be >= 1")
    if not 0.0 < positive_rate < 1.0:
        raise ValueError("positive_rate must be in (0, 1)")

    base = datetime(2025, 6, 1, 12, 0, tzinfo=UTC)
    records: list[PullRequestRecord] = []
    # Deterministic positive indices via hash of seed
    positives = {
        i
        for i in range(n_samples)
        if (int(hashlib.md5(f"{seed}:{i}".encode()).hexdigest(), 16) % 1000) / 1000.0
        < positive_rate
    }
    # Ensure at least one of each class
    positives.add(0)
    if n_samples > 1:
        positives.discard(1)

    for i in range(n_samples):
        repo = REPOS[i % len(REPOS)]
        author = AUTHORS[i % len(AUTHORS)]
        files = 1 + (i * 3 + seed) % 8
        added = 5 + (i * 7 + seed) % 120
        deleted = 1 + (i * 5 + seed) % 40
        risky = i in positives
        ts = base + timedelta(days=(i // len(REPOS)) * 2, hours=i % 17)
        records.append(
            PullRequestRecord(
                repository=repo,
                pull_request_id=1000 + i,
                commit_sha=_sha(f"commit:{seed}:{i}"),
                parent_sha=_sha(f"parent:{seed}:{i}"),
                author=author,
                author_tenure_days=float(10 + (i * 13) % 800),
                files_changed=files,
                lines_added=added,
                lines_deleted=deleted,
                file_churn=float(added + deleted),
                diff_text=_diff_text(i, files, added, deleted, risky),
                bug_introducing_label=1 if risky else 0,
                label_source="synthetic_demo",
                timestamp=ts,
                is_synthetic=True,
            )
        )
    return records


def records_to_frame(records: list[PullRequestRecord]) -> pd.DataFrame:
    """Convert records to a DataFrame with required columns."""
    rows = [r.model_dump(mode="python") for r in records]
    df = pd.DataFrame(rows)
    return df[REQUIRED_COLUMNS]


def validate_dataset(df: pd.DataFrame) -> dict[str, Any]:
    """Validate PR dataset invariants and return a class-distribution report."""
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    if df["commit_sha"].duplicated().any():
        dupes = df.loc[df["commit_sha"].duplicated(), "commit_sha"].tolist()
        raise ValueError(f"Duplicate commit_sha values: {dupes[:5]}")

    if df[REQUIRED_COLUMNS].isna().any().any():
        raise ValueError("Dataset contains missing required values")

    labels = set(df["bug_introducing_label"].unique().tolist())
    if not labels.issubset({0, 1}):
        raise ValueError(f"Labels must be binary 0/1, got {labels}")

    empty_diff = df["diff_text"].astype(str).str.strip().eq("")
    if empty_diff.any():
        raise ValueError("Found empty diff_text rows")

    if not df["is_synthetic"].all():
        raise ValueError("Demo dataset rows must set is_synthetic=True")

    if not (df["label_source"] == "synthetic_demo").all():
        raise ValueError("Demo dataset label_source must be synthetic_demo")

    n = len(df)
    pos = int((df["bug_introducing_label"] == 1).sum())
    neg = n - pos
    report = {
        "n_rows": n,
        "n_positive": pos,
        "n_negative": neg,
        "positive_rate": round(pos / n, 4) if n else 0.0,
        "n_repositories": int(df["repository"].nunique()),
        "is_synthetic": True,
        "label_source": "synthetic_demo",
    }
    logger.info("dataset_validation_ok %s", report)
    return report


def write_demo_dataset(
    output_dir: Path | str,
    *,
    n_samples: int = 120,
    seed: int = 42,
    positive_rate: float = 0.35,
) -> tuple[Path, dict[str, Any]]:
    """Generate, validate, and write the demo dataset + report."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    records = generate_demo_records(n_samples, seed=seed, positive_rate=positive_rate)
    df = records_to_frame(records)
    report = validate_dataset(df)

    parquet_path = out / "dataset.parquet"
    csv_path = out / "dataset.csv"
    report_path = out / "validation_report.json"

    df.to_parquet(parquet_path, index=False)
    df.to_csv(csv_path, index=False)

    import json

    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    readme = out / "README.md"
    readme.write_text(
        "# Synthetic demo dataset\n\n"
        "All rows are **synthetic** (`is_synthetic=true`, "
        "`label_source=synthetic_demo`).\n"
        "Do not treat this as mined open-source history.\n",
        encoding="utf-8",
    )
    return parquet_path, report
