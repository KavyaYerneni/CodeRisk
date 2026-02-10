import runpy
import sys
from pathlib import Path


def test_dry_run_prints_plan(capsys, tmp_path) -> None:
    script = Path("scripts/mine_repositories.py")
    sys.argv = [str(script), "--repo", "acme/demo", "--dry-run", "--output-dir", str(tmp_path)]
    try:
        runpy.run_path(str(script), run_name="__main__")
    except SystemExit as exc:
        assert exc.code in (0, None)
    out = capsys.readouterr().out
    assert "acme/demo" in out
