"""Tests for JSONL mining cache."""

from __future__ import annotations

from pathlib import Path

from coderisk.data.cache import JsonlCache


def test_write_read_roundtrip(tmp_path: Path) -> None:
    cache = JsonlCache(tmp_path)
    rows = [{"repository": "a/b", "number": 1}, {"repository": "a/b", "number": 2}]
    path = cache.write_rows("a/b", rows)
    assert path.exists()
    assert cache.exists("a/b")
    assert cache.read_rows("a/b") == rows


def test_append_and_iter(tmp_path: Path) -> None:
    cache = JsonlCache(tmp_path)
    cache.append_row("x/y", {"number": 3})
    cache.append_row("x/y", {"number": 4})
    assert [r["number"] for r in cache.iter_all()] == [3, 4]
