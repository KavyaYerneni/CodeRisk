"""Filesystem JSONL cache for mining downloads."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator


class JsonlCache:
    """Append-only JSONL cache keyed by repository slug."""

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def path_for(self, repo: str, kind: str = "pulls") -> Path:
        safe = repo.replace("/", "__")
        return self.root / f"{safe}_{kind}.jsonl"

    def exists(self, repo: str, kind: str = "pulls") -> bool:
        return self.path_for(repo, kind).exists()

    def write_rows(self, repo: str, rows: list[dict[str, Any]], *, kind: str = "pulls") -> Path:
        path = self.path_for(repo, kind)
        with path.open("w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, sort_keys=True) + "\n")
        return path

    def append_row(self, repo: str, row: dict[str, Any], *, kind: str = "pulls") -> None:
        path = self.path_for(repo, kind)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, sort_keys=True) + "\n")

    def read_rows(self, repo: str, *, kind: str = "pulls") -> list[dict[str, Any]]:
        path = self.path_for(repo, kind)
        if not path.exists():
            return []
        rows: list[dict[str, Any]] = []
        with path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows

    def iter_all(self, *, kind: str = "pulls") -> Iterator[dict[str, Any]]:
        for path in sorted(self.root.glob(f"*_{kind}.jsonl")):
            with path.open(encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        yield json.loads(line)
