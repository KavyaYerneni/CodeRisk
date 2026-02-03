#!/usr/bin/env python3
"""Build the CodeRisk dataset (demo mode by default)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running without install during early bootstrap
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from coderisk.config import load_config
from coderisk.data.demo_dataset import write_demo_dataset
from coderisk.logging_config import get_logger, setup_logging


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build CodeRisk datasets")
    parser.add_argument("--mode", choices=["demo"], default="demo")
    parser.add_argument("--config", default="configs/demo.yaml")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--n-samples", type=int, default=None)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args(argv)

    cfg = load_config(args.config)
    setup_logging(level=cfg.logging.level)
    logger = get_logger(__name__)

    if args.mode != "demo":
        raise SystemExit(f"Unsupported mode: {args.mode}")

    n = args.n_samples or int(cfg.dataset.get("n_samples", 120))
    seed = args.seed if args.seed is not None else cfg.seed
    out = args.output_dir or cfg.dataset.get("output_dir", "data/processed/demo")
    positive_rate = float(cfg.dataset.get("positive_rate", 0.35))

    path, report = write_demo_dataset(
        out, n_samples=n, seed=seed, positive_rate=positive_rate
    )
    logger.info("wrote_demo_dataset path=%s report=%s", path, report)
    print(f"wrote {path} n={report['n_rows']} positive_rate={report['positive_rate']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
