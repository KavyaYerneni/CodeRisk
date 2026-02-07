"""Unit tests for GitHub client (no network)."""

from __future__ import annotations

import json

import httpx

from coderisk.data.github_client import GitHubClient


def test_list_pull_requests_mocked() -> None:
    payload = [
        {
            "number": 1,
            "title": "fix bug",
            "user": {"login": "alice"},
            "merged_at": "2025-01-01T00:00:00Z",
            "created_at": "2024-12-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z",
            "base": {"sha": "abc"},
            "head": {"sha": "def"},
        }
    ]

    def fake_request(method: str, path: str, params=None):  # noqa: ANN001
        assert method == "GET"
        assert path == "/repos/acme/demo/pulls"
        request = httpx.Request("GET", "https://api.github.com/repos/acme/demo/pulls")
        return httpx.Response(200, json=payload, request=request)

    client = GitHubClient(token=None, request_fn=fake_request)
    rows = client.list_pull_requests("acme/demo", limit=5)
    assert len(rows) == 1
    assert rows[0]["number"] == 1
    assert rows[0]["repository"] == "acme/demo"
    assert json.dumps(rows[0])  # serializable
