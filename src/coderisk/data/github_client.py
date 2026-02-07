"""GitHub REST client with retries, pagination helpers, and test seams."""

from __future__ import annotations

import os
import time
from collections.abc import Callable
from typing import Any

import httpx

from coderisk.logging_config import get_logger

logger = get_logger(__name__)


def load_token_from_env() -> str | None:
    """Load GitHub token from environment; never log the value."""
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or None


class GitHubClient:
    """Minimal GitHub pulls client.

    Network calls are injectable via ``transport`` / ``request_fn`` for unit tests.
    """

    def __init__(
        self,
        token: str | None = None,
        *,
        base_url: str = "https://api.github.com",
        max_retries: int = 3,
        request_fn: Callable[..., httpx.Response] | None = None,
    ) -> None:
        self.token = token
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self._request_fn = request_fn
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "coderisk-miner",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._client = httpx.Client(base_url=self.base_url, headers=headers, timeout=30.0)

    def close(self) -> None:
        self._client.close()

    def _get(self, path: str, params: dict[str, Any] | None = None) -> httpx.Response:
        last_exc: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                if self._request_fn is not None:
                    response = self._request_fn("GET", path, params=params)
                else:
                    response = self._client.get(path, params=params)
                if response.status_code == 403 and response.headers.get(
                    "X-RateLimit-Remaining"
                ) == "0":
                    reset = int(response.headers.get("X-RateLimit-Reset", "0"))
                    sleep_for = max(0, reset - int(time.time())) + 1
                    logger.warning("rate_limited sleep_s=%s", sleep_for)
                    time.sleep(min(sleep_for, 5))
                    continue
                if response.status_code >= 400:
                    response.raise_for_status()
                return response
            except Exception as exc:  # noqa: BLE001 — retried then re-raised
                last_exc = exc
                logger.warning("github_get_retry attempt=%s error=%s", attempt + 1, exc)
                time.sleep(0.2 * (attempt + 1))
        assert last_exc is not None
        raise last_exc

    def list_pull_requests(self, repo: str, *, limit: int = 10) -> list[dict[str, Any]]:
        """Fetch up to ``limit`` pull requests for ``owner/name``."""
        if "/" not in repo:
            raise ValueError("repo must be owner/name")
        owner, name = repo.split("/", 1)
        results: list[dict[str, Any]] = []
        page = 1
        per_page = min(100, max(1, limit))
        while len(results) < limit:
            response = self._get(
                f"/repos/{owner}/{name}/pulls",
                params={"state": "all", "per_page": per_page, "page": page},
            )
            batch = response.json()
            if not batch:
                break
            for item in batch:
                results.append(
                    {
                        "repository": repo,
                        "number": item.get("number"),
                        "title": item.get("title"),
                        "user": (item.get("user") or {}).get("login"),
                        "merged_at": item.get("merged_at"),
                        "created_at": item.get("created_at"),
                        "updated_at": item.get("updated_at"),
                        "base_sha": (item.get("base") or {}).get("sha"),
                        "head_sha": (item.get("head") or {}).get("sha"),
                    }
                )
                if len(results) >= limit:
                    break
            if len(batch) < per_page:
                break
            page += 1
        return results
