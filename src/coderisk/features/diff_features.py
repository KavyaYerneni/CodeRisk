"""Diff / code-change feature extraction."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from coderisk.data.git_parser import parse_unified_diff

TEST_HINTS = ("test", "tests", "spec", "_test.", ".test.")
DOC_HINTS = (".md", ".rst", ".txt", "docs/", "readme")


def _ext_counts(paths: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for path in paths:
        ext = Path(path).suffix.lower() or "<none>"
        counts[ext] = counts.get(ext, 0) + 1
    return counts


def extract_diff_features(diff_text: str, *, files_changed: int | None = None) -> dict[str, Any]:
    """Extract numeric features from a unified diff string."""
    stats = parse_unified_diff(diff_text)
    paths = stats.paths
    exts = _ext_counts(paths)
    renamed = len(re.findall(r"^rename from ", diff_text, flags=re.MULTILINE))
    test_files = sum(1 for p in paths if any(h in p.lower() for h in TEST_HINTS))
    doc_files = sum(1 for p in paths if any(h in p.lower() for h in DOC_HINTS))
    added = stats.lines_added
    deleted = stats.lines_deleted
    changed = added + deleted
    ratio = (added / deleted) if deleted else float(added)
    return {
        "feat_files_changed": float(files_changed if files_changed is not None else stats.files_changed),
        "feat_lines_added": float(added),
        "feat_lines_deleted": float(deleted),
        "feat_lines_changed": float(changed),
        "feat_hunks": float(stats.hunks),
        "feat_diff_length": float(len(diff_text)),
        "feat_renamed_files": float(renamed),
        "feat_test_file_count": float(test_files),
        "feat_doc_file_count": float(doc_files),
        "feat_added_deleted_ratio": float(ratio),
        "feat_file_churn": float(changed),
        "feat_max_path_len": float(max((len(p) for p in paths), default=0)),
        "feat_ext_py": float(exts.get(".py", 0)),
        "feat_ext_js": float(exts.get(".js", 0) + exts.get(".ts", 0)),
        "feat_ext_other": float(sum(v for k, v in exts.items() if k not in {".py", ".js", ".ts"})),
    }
