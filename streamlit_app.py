"""Streamlit Community Cloud entry point.

Deploy this file as the main module on Streamlit Cloud (default path: streamlit_app.py).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from app.ui.streamlit_app import main

main()
