"""GitHub rate-limit helpers."""

from __future__ import annotations

import time
from collections.abc import Mapping


def seconds_until_reset(headers: Mapping[str, str], *, now: float | None = None) -> float:
    """Return seconds to sleep until X-RateLimit-Reset, capped for tests."""
    remaining = headers.get("X-RateLimit-Remaining") or headers.get("x-ratelimit-remaining")
    reset = headers.get("X-RateLimit-Reset") or headers.get("x-ratelimit-reset")
    if remaining is None or reset is None:
        return 0.0
    try:
        if int(remaining) > 0:
            return 0.0
        reset_ts = int(reset)
    except ValueError:
        return 0.0
    current = time.time() if now is None else now
    return max(0.0, float(reset_ts - current) + 1.0)


def should_retry_status(status_code: int) -> bool:
    return status_code in {403, 429, 500, 502, 503, 504}
