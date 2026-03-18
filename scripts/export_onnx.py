#!/usr/bin/env python3
"""Export CodeBERT to ONNX and validate against PyTorch."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from coderisk.inference.onnx_export import export_codebert_onnx, validate_onnx_parity
from coderisk.logging_config import get_logger, setup_logging


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", default="artifacts/codebert")
    parser.add_argument("--output", default="artifacts/codebert/model.onnx")
    parser.add_argument("--max-length", type=int, default=256)
    args = parser.parse_args(argv)
    setup_logging()
    logger = get_logger(__name__)

    model_dir = Path(args.model_dir)
    if not model_dir.exists():
        raise SystemExit(f"Model missing: {model_dir}")

    onnx_path = export_codebert_onnx(model_dir, args.output, max_length=args.max_length)
    report = validate_onnx_parity(model_dir, onnx_path, max_length=args.max_length)
    out = Path(args.output).with_suffix(".parity.json")
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    logger.info("onnx_parity %s", report)
    print(json.dumps(report))
    if not report["ok"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
