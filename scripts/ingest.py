#!/usr/bin/env python3
"""CLI entry point for dataset ingestion."""

import sys

from app.ingestion.pipeline import main

if __name__ == "__main__":
    sys.exit(main())
