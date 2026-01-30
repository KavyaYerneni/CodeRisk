"""Structured logging setup for CodeRisk."""

from __future__ import annotations

import logging
import sys
from typing import Any


def setup_logging(level: str = "INFO", json_logs: bool = False) -> None:
    """Configure root logger once.

    Args:
        level: Logging level name (e.g. INFO, DEBUG).
        json_logs: If True, emit simple key=value style lines suitable for scraping.
    """
    root = logging.getLogger()
    if root.handlers:
        root.setLevel(getattr(logging, level.upper(), logging.INFO))
        return

    handler = logging.StreamHandler(sys.stderr)
    if json_logs:
        formatter = logging.Formatter(
            '{"level":"%(levelname)s","logger":"%(name)s","message":%(message)s}'
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    handler.setFormatter(formatter)
    root.addHandler(handler)
    root.setLevel(getattr(logging, level.upper(), logging.INFO))


def get_logger(name: str) -> logging.Logger:
    """Return a named logger."""
    return logging.getLogger(name)


def log_extra(**kwargs: Any) -> str:
    """Format structured fields for a log message body."""
    return " ".join(f"{k}={v!r}" for k, v in kwargs.items())
