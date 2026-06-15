from __future__ import annotations

import os


def apply_streamlit_secrets() -> None:
    """Map Streamlit root-level secrets into os.environ for pydantic-settings."""
    try:
        import streamlit as st
    except ImportError:
        return

    try:
        secrets = st.secrets
    except Exception:
        return

    for key, value in secrets.items():
        if isinstance(value, (str, int, float, bool)):
            os.environ.setdefault(str(key).upper(), str(value))
