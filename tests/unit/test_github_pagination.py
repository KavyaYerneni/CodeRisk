"""Pagination coverage for GitHubClient."""

from __future__ import annotations

import httpx

from coderisk.data.github_client import GitHubClient


def test_paginates_until_limit() -> None:
    pages = {
        1: [{"number": i, "title": f"t{i}", "user": {"login": "a"}, "base": {"sha": "b"}, "head": {"sha": "c"}} for i in range(1, 3)],
        2: [{"number": i, "title": f"t{i}", "user": {"login": "a"}, "base": {"sha": "b"}, "head": {"sha": "c"}} for i in range(3, 5)],
    }

    def fake(method: str, path: str, params=None):  # noqa: ANN001
        page = int((params or {}).get("page", 1))
        req = httpx.Request("GET", f"https://api.github.com{path}")
        return httpx.Response(200, json=pages.get(page, []), request=req)

    client = GitHubClient(request_fn=fake)
    rows = client.list_pull_requests("acme/demo", limit=3)
    assert [r["number"] for r in rows] == [1, 2, 3]
