#!/usr/bin/env python3
"""GitHub repository mining CLI (Phase 3 start — dry-run / mocked-safe)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from coderisk.data.github_client import GitHubClient, load_token_from_env
from coderisk.logging_config import get_logger, setup_logging


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mine PR metadata from GitHub")
    parser.add_argument("--repo", help="owner/name for a single repository")
    parser.add_argument("--repos-file", help="Text file with one owner/name per line")
    parser.add_argument("--limit", type=int, default=10, help="Max PRs per repo")
    parser.add_argument("--output-dir", default="data/raw")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args(argv)

    setup_logging()
    logger = get_logger(__name__)

    repos: list[str] = []
    if args.repo:
        repos.append(args.repo)
    if args.repos_file:
        repos.extend(
            line.strip()
            for line in Path(args.repos_file).read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        )
    if not repos:
        raise SystemExit("Provide --repo or --repos-file")

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        plan = {"repos": repos, "limit": args.limit, "output_dir": str(out)}
        print(json.dumps(plan, indent=2))
        logger.info("dry_run_plan %s", plan)
        return 0

    token = load_token_from_env()
    client = GitHubClient(token=token)
    for repo in repos:
        path = out / f"{repo.replace('/', '__')}_pulls.jsonl"
        if args.resume and path.exists():
            logger.info("resume_skip existing=%s", path)
            continue
        rows = client.list_pull_requests(repo, limit=args.limit)
        with path.open("w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")
        logger.info("wrote_pulls repo=%s path=%s n=%s", repo, path, len(rows))
        print(f"wrote {path} n={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
