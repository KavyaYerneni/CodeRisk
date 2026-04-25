"""Text packing for CodeBERT inputs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def build_codebert_text(row: Mapping[str, Any], *, max_diff_chars: int = 2000) -> str:
    """Build controlled text: DIFF + metadata fields separated by [SEP]."""
    diff = str(row.get("diff_text", ""))[:max_diff_chars]
    files = row.get("files_changed", "")
    added = row.get("lines_added", "")
    deleted = row.get("lines_deleted", "")
    author = row.get("author", "")
    return (
        f"DIFF: {diff} [SEP] FILES_CHANGED: {files} [SEP] "
        f"LINES_ADDED: {added} [SEP] LINES_DELETED: {deleted} [SEP] AUTHOR: {author}"
    )
