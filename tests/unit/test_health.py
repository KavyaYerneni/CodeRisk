"""Health CLI smoke tests."""

from __future__ import annotations

from coderisk import __version__
from coderisk.cli import cmd_health, cmd_version


def test_version(capsys) -> None:
    assert cmd_version(None) == 0  # type: ignore[arg-type]
    assert capsys.readouterr().out.strip() == __version__


def test_health(capsys) -> None:
    assert cmd_health(None) == 0  # type: ignore[arg-type]
    out = capsys.readouterr().out
    assert "ok coderisk=" in out
