from __future__ import annotations

from pathlib import Path

import streamlit as st

from config.settings import settings
from services.extraction_service import ExtractionService
from ui.dashboard import render_page_header


def render(service: ExtractionService) -> None:
    render_page_header("System Status")
    http = getattr(service.client, "http", None)
    access_token = getattr(http, "access_token", None)
    token_exp = getattr(http, "access_token_exp", 0)
    processing_log = settings.logs_dir / "processing.log"

    st.metric("DBD Auth Status", "Available" if access_token else "Not initialized")
    st.metric("Chrome Auth Status", _chrome_status())
    st.metric("JWT Available", "Yes" if access_token else "No")
    st.metric("Token Refresh Count", _count_occurrences(processing_log, "anonymous DBD token refreshed"))
    st.metric("Last Extraction Time", _last_extraction_time())

    st.subheader("Runtime")
    st.table(
        [
            {"Setting": "Cache Directory", "Value": str(settings.cache_dir)},
            {"Setting": "Cache Size", "Value": _format_bytes(_directory_size(settings.cache_dir))},
            {"Setting": "Chrome Channel", "Value": settings.dbd_playwright_channel},
            {"Setting": "Chrome Mode", "Value": "headless" if settings.dbd_playwright_headless else "headed"},
            {"Setting": "Chrome Profile", "Value": str(settings.dbd_chrome_profile_dir)},
            {"Setting": "JWT Expiration", "Value": token_exp or "NULL"},
        ]
    )


def _chrome_status() -> str:
    mode = "headless" if settings.dbd_playwright_headless else "headed"
    return f"{settings.dbd_playwright_channel} / {mode}"


def _last_extraction_time() -> str:
    value = st.session_state.get("last_extraction_time")
    if value is None:
        return "NULL"
    return f"{float(value):.1f}s"


def _count_occurrences(path: Path, needle: str) -> int:
    if not path.exists():
        return 0
    return path.read_text(encoding="utf-8", errors="ignore").count(needle)


def _directory_size(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(file.stat().st_size for file in path.rglob("*") if file.is_file())


def _format_bytes(value: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{value} B"
