#!/usr/bin/env python3
"""Ensure processed restaurant data exists (for local or container bootstrap)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.deploy.bootstrap import DatasetBootstrapError, ensure_dataset  # noqa: E402


def main() -> int:
    try:
        path = ensure_dataset(allow_ingest=True)
        print(f"Dataset ready: {path}")
        return 0
    except DatasetBootstrapError as exc:
        print(f"Bootstrap failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
