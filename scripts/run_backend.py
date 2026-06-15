#!/usr/bin/env python3
"""Launch the FastAPI backend (uvicorn)."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV_UVICORN = ROOT / ".venv" / "bin" / "uvicorn"


def main() -> int:
    uvicorn = VENV_UVICORN if VENV_UVICORN.exists() else "uvicorn"
    cmd = [
        str(uvicorn),
        "app.main:app",
        "--reload",
        "--app-dir",
        str(ROOT / "src"),
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
    ]
    return subprocess.call(cmd, cwd=ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
