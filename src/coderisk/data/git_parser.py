"""Lightweight helpers for parsing unified diffs and commit metadata."""

from __future__ import annotations

import re
from dataclasses import dataclass

DIFF_FILE_RE = re.compile(r"^diff --git a/(.+?) b/(.+)$", re.MULTILINE)
HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+\d+(?:,\d+)? @@", re.MULTILINE)


@dataclass
class DiffStats:
    files_changed: int
    lines_added: int
    lines_deleted: int
    hunks: int
    paths: list[str]


def parse_unified_diff(diff_text: str) -> DiffStats:
    """Parse a unified diff into coarse change statistics."""
    paths = [m.group(2) for m in DIFF_FILE_RE.finditer(diff_text)]
    added = deleted = 0
    for line in diff_text.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            added += 1
        elif line.startswith("-") and not line.startswith("---"):
            deleted += 1
    hunks = len(HUNK_RE.findall(diff_text))
    return DiffStats(
        files_changed=len(paths) or (1 if diff_text.strip() else 0),
        lines_added=added,
        lines_deleted=deleted,
        hunks=hunks,
        paths=paths,
    )


def is_merge_commit_message(message: str) -> bool:
    """Heuristic: treat classic merge subjects as merges."""
    return message.strip().lower().startswith("merge ")
