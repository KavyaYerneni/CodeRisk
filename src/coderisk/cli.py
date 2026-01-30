"""Command-line entry points for CodeRisk."""

from __future__ import annotations

import argparse
import sys

from coderisk import __version__
from coderisk.config import get_env_settings, load_config
from coderisk.logging_config import get_logger, setup_logging


def cmd_health(_: argparse.Namespace) -> int:
    """Print a health check and exit 0 if the package imports cleanly."""
    logger = get_logger(__name__)
    env = get_env_settings()
    cfg = load_config("configs/demo.yaml")
    logger.info(
        "health_ok version=%s seed=%s model_dir=%s",
        __version__,
        cfg.seed,
        env.coderisk_model_dir,
    )
    print(f"ok coderisk={__version__} seed={cfg.seed}")
    return 0


def cmd_version(_: argparse.Namespace) -> int:
    print(__version__)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="coderisk", description="CodeRisk CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    health = sub.add_parser("health", help="Run a local health check")
    health.set_defaults(func=cmd_health)

    version = sub.add_parser("version", help="Print package version")
    version.set_defaults(func=cmd_version)
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    setup_logging(level=get_env_settings().coderisk_log_level)
    code = args.func(args)
    sys.exit(code)


if __name__ == "__main__":
    main()
