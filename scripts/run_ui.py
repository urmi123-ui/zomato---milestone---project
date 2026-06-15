#!/usr/bin/env python3
"""Launch the Streamlit presentation layer."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "src" / "app" / "ui" / "streamlit_app.py"
SRC_PATH = ROOT / "src"


def main() -> int:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_PATH)
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(APP_PATH),
        "--server.headless",
        "true",
    ]
    return subprocess.call(cmd, env=env)


if __name__ == "__main__":
    raise SystemExit(main())
