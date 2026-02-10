from coderisk.data.rate_limit import seconds_until_reset, should_retry_status


def test_seconds_until_reset() -> None:
    headers = {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1000"}
    assert seconds_until_reset(headers, now=990.0) == 11.0
    headers2 = {"X-RateLimit-Remaining": "5", "X-RateLimit-Reset": "1000"}
    assert seconds_until_reset(headers2, now=990.0) == 0.0


def test_retry_statuses() -> None:
    assert should_retry_status(429)
    assert not should_retry_status(404)
