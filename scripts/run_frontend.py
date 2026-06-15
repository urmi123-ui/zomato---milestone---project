#!/usr/bin/env python3
"""Launch the DineAI React frontend (Vite dev server)."""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"


def main() -> int:
    npm = shutil.which("npm")
    if npm is None:
        print("npm is required to run the frontend. Install Node.js first.", file=sys.stderr)
        return 1

    if not (FRONTEND / "node_modules").exists():
        print("Installing frontend dependencies…")
        install = subprocess.run([npm, "install"], cwd=FRONTEND)
        if install.returncode != 0:
            return install.returncode

    return subprocess.call([npm, "run", "dev"], cwd=FRONTEND)


if __name__ == "__main__":
    raise SystemExit(main())
