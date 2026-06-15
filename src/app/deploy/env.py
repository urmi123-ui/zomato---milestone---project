from __future__ import annotations

import os


def apply_streamlit_secrets() -> None:
    """Map Streamlit root-level secrets into os.environ for pydantic-settings."""
    try:
        import streamlit as st
    except ImportError:
        return

    try:
        for key, value in st.secrets.items():
            if isinstance(value, (str, int, float, bool)):
                os.environ.setdefault(str(key).upper(), str(value))
    except Exception:
        return
