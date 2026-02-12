"""SZZ tests using a tiny temporary git repository."""

from __future__ import annotations

import subprocess
from pathlib import Path

from coderisk.data.szz import is_bug_fixing_message, run_szz


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "dev@example.com")
    _git(repo, "config", "user.name", "Dev")
    (repo / "app.py").write_text("x = 1\ny = 2\n", encoding="utf-8")
    _git(repo, "add", "app.py")
    _git(repo, "commit", "-m", "initial")
    # buggy change
    (repo / "app.py").write_text("x = 1\ny = 0  # bug\n", encoding="utf-8")
    _git(repo, "add", "app.py")
    _git(repo, "commit", "-m", "introduce zero")
    # fix
    (repo / "app.py").write_text("x = 1\ny = 2  # fixed\n", encoding="utf-8")
    _git(repo, "add", "app.py")
    _git(repo, "commit", "-m", "fix division risk")
    return repo


def test_keyword_detection() -> None:
    assert is_bug_fixing_message("fix null pointer")
    assert not is_bug_fixing_message("add feature flag")


def test_szz_finds_blamed_commit(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    links = run_szz(repo)
    assert links, "expected at least one SZZ link"
    assert all(link.reason for link in links)
    assert any("app.py" in link.file_path for link in links)
