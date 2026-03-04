"""Write JSON/Markdown evaluation reports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_json_report(path: Path | str, payload: dict[str, Any]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    return path


def write_markdown_report(path: Path | str, title: str, metrics: dict[str, Any]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {title}", "", "| Metric | Value |", "|---|---|"]
    for key, value in metrics.items():
        if isinstance(value, dict):
            continue
        lines.append(f"| `{key}` | {value} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
