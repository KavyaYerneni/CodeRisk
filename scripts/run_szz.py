#!/usr/bin/env python3
"""Run baseline SZZ on a local git repository and write JSONL links."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from coderisk.data.szz import links_to_dicts, run_szz
from coderisk.logging_config import get_logger, setup_logging


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run baseline SZZ")
    parser.add_argument("--repo", required=True, help="Path to local git repository")
    parser.add_argument("--output", default="data/interim/szz_links.jsonl")
    args = parser.parse_args(argv)

    setup_logging()
    logger = get_logger(__name__)
    repo = Path(args.repo)
    links = run_szz(repo)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for row in links_to_dicts(links):
            f.write(json.dumps(row) + "\n")
    logger.info("wrote_szz path=%s n=%s", out, len(links))
    print(f"wrote {out} n={len(links)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
