"""Pagination coverage for GitHubClient."""

from __future__ import annotations

import httpx

from coderisk.data.github_client import GitHubClient


def test_paginates_until_limit() -> None:
    def make(n: int) -> dict:
        return {
            "number": n,
            "title": f"t{n}",
            "user": {"login": "a"},
            "base": {"sha": "b"},
            "head": {"sha": "c"},
        }

    pages = {
        1: [make(i) for i in range(1, 101)],
        2: [make(i) for i in range(101, 201)],
    }

    def fake(method: str, path: str, params=None):  # noqa: ANN001
        page = int((params or {}).get("page", 1))
        req = httpx.Request("GET", f"https://api.github.com{path}")
        return httpx.Response(200, json=pages.get(page, []), request=req)

    client = GitHubClient(request_fn=fake)
    rows = client.list_pull_requests("acme/demo", limit=105)
    assert len(rows) == 105
    assert rows[0]["number"] == 1
    assert rows[-1]["number"] == 105
