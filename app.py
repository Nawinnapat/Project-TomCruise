from __future__ import annotations

import streamlit as st

from config.settings import settings
from services.extraction_service import ExtractionService
from ui import batch_upload, log_viewer, single_search, status_page
from ui.dashboard import render_results_table
from utils.logging import setup_logging


def main() -> None:
    setup_logging()
    st.set_page_config(page_title="Project TomCruise", layout="wide")
    st.sidebar.title("Project TomCruise")
    page = st.sidebar.radio(
        "Navigation",
        ["Single Company Search", "Batch Processing", "Results", "System Status", "Log Viewer"],
    )
    service = _service()
    output_dir = settings.output_dir / "streamlit"

    if page == "Single Company Search":
        single_search.render(service, output_dir)
    elif page == "Batch Processing":
        batch_upload.render(service, output_dir)
    elif page == "Results":
        st.title("Results")
        render_results_table(st.session_state.get("latest_records", []), key_prefix="latest")
    elif page == "System Status":
        status_page.render(service)
    else:
        log_viewer.render()


@st.cache_resource
def _service() -> ExtractionService:
    return ExtractionService()


if __name__ == "__main__":
    main()
