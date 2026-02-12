"""Baseline SZZ-style bug-introducing commit labeling.

This is a transparent heuristic, not ground truth. Labels are noisy.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from coderisk.logging_config import get_logger

logger = get_logger(__name__)

BUG_FIX_KEYWORDS = (
    "fix",
    "bug",
    "defect",
    "hotfix",
    "patch",
    "resolve",
    "closes",
    "fixes",
)


@dataclass
class SzzLink:
    bug_fixing_commit: str
    blamed_commit: str
    file_path: str
    line_number: int
    confidence: float
    reason: str


def is_bug_fixing_message(message: str) -> bool:
    """Return True if commit message looks like a bug fix."""
    lower = message.lower()
    return any(k in lower for k in BUG_FIX_KEYWORDS)


def _run_git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout


def list_commits(repo: Path, *, ignore_merges: bool = True) -> list[dict[str, str]]:
    """List commits as {sha, parents, subject}."""
    fmt = "%H%x09%P%x09%s"
    args = ["log", f"--format={fmt}"]
    if ignore_merges:
        args.append("--no-merges")
    out = _run_git(repo, *args)
    commits: list[dict[str, str]] = []
    for line in out.splitlines():
        sha, parents, subject = line.split("\t", 2)
        commits.append({"sha": sha, "parents": parents, "subject": subject})
    return commits


def deleted_lines_in_commit(repo: Path, sha: str) -> list[tuple[str, int, str]]:
    """Return (path, parent_line_number, line_text) for deleted/modified lines."""
    # Unified diff vs first parent
    try:
        diff = _run_git(repo, "show", "--format=", "--unified=0", sha)
    except RuntimeError as exc:
        logger.warning("diff_unavailable sha=%s err=%s", sha, exc)
        return []

    results: list[tuple[str, int, str]] = []
    path = ""
    old_line = 0
    for line in diff.splitlines():
        if line.startswith("diff --git "):
            m = re.search(r" b/(.+)$", line)
            path = m.group(1) if m else ""
            continue
        if line.startswith("Binary files "):
            path = ""
            continue
        if line.startswith("@@"):
            # @@ -old_start,old_count +new_start,new_count @@
            m = re.search(r"@@ -(\d+)(?:,(\d+))?", line)
            if not m:
                continue
            old_line = int(m.group(1))
            continue
        if not path:
            continue
        if line.startswith("-") and not line.startswith("---"):
            results.append((path, old_line, line[1:]))
            old_line += 1
        elif line.startswith("+") and not line.startswith("+++"):
            continue
        else:
            # context shouldn't appear with unified=0, but be safe
            old_line += 1
    return results


def blame_line(repo: Path, parent_sha: str, path: str, line_number: int) -> str | None:
    """Blame a single line on the parent tree; return introducing commit or None."""
    try:
        out = _run_git(
            repo,
            "blame",
            "-L",
            f"{line_number},{line_number}",
            "--porcelain",
            parent_sha,
            "--",
            path,
        )
    except RuntimeError as exc:
        logger.warning("blame_failed path=%s line=%s err=%s", path, line_number, exc)
        return None
    first = out.splitlines()[0] if out.strip() else ""
    if not first:
        return None
    return first.split()[0]


def run_szz(
    repo: Path,
    *,
    ignore_merges: bool = True,
) -> list[SzzLink]:
    """Run a baseline SZZ pass over a local git repository."""
    links: list[SzzLink] = []
    for commit in list_commits(repo, ignore_merges=ignore_merges):
        if not is_bug_fixing_message(commit["subject"]):
            continue
        parents = commit["parents"].split()
        if not parents:
            continue
        parent = parents[0]
        for path, line_no, _text in deleted_lines_in_commit(repo, commit["sha"]):
            if path.endswith((".png", ".jpg", ".gif", ".pdf", ".zip")):
                continue
            blamed = blame_line(repo, parent, path, line_no)
            if not blamed or blamed.startswith("0000"):
                continue
            links.append(
                SzzLink(
                    bug_fixing_commit=commit["sha"],
                    blamed_commit=blamed,
                    file_path=path,
                    line_number=line_no,
                    confidence=0.5,
                    reason="keyword_fix_deleted_line_blame",
                )
            )
    logger.info("szz_links n=%s repo=%s", len(links), repo)
    return links


def links_to_dicts(links: list[SzzLink]) -> list[dict[str, Any]]:
    return [asdict(link) for link in links]
