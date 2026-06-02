from __future__ import annotations

import streamlit as st

from config.settings import settings
from ui.dashboard import render_page_header


LOG_FILES = {
    "processing.log": settings.logs_dir / "processing.log",
    "error.log": settings.logs_dir / "error.log",
    "validation.log": settings.logs_dir / "validation.log",
}


def render() -> None:
    render_page_header("Log Viewer")
    selected = st.selectbox("Log File", list(LOG_FILES.keys()))
    lines = st.slider("Latest entries", min_value=20, max_value=500, value=100, step=20)
    path = LOG_FILES[selected]
    if not path.exists():
        st.info(f"{selected} does not exist yet.")
        return
    entries = path.read_text(encoding="utf-8", errors="ignore").splitlines()[-lines:]
    st.code("\n".join(entries) or "No log entries.", language="text")
