from __future__ import annotations

from pathlib import Path

import streamlit as st

from config.settings import settings
from models.company import CompanyRecord
from services.extraction_service import ExtractionService, load_inputs
from ui.dashboard import (
    elapsed_since,
    render_downloads,
    render_page_header,
    render_results_table,
    render_summary,
    start_timer,
)


def render(service: ExtractionService, output_dir: Path) -> None:
    render_page_header("Batch Processing", "Upload a CSV or XLSX file with company_name and/or juristic_id columns.")
    uploaded_file = st.file_uploader("Upload File", type=["csv", "xlsx", "xlsm"])
    years_text = st.text_input("Fiscal Years", placeholder="2568,2567")

    if st.button("Process", type="primary", disabled=uploaded_file is None):
        assert uploaded_file is not None
        upload_path = _save_upload(uploaded_file)
        years = [year.strip() for year in years_text.split(",") if year.strip()]
        inputs = load_inputs(upload_path)
        progress = st.progress(0)
        started_at = start_timer()
        records: list[CompanyRecord] = []
        status = st.empty()

        for index, company_input in enumerate(inputs, start=1):
            status.write(f"Processing {index} of {len(inputs)}")
            records.extend(service.extract_many([company_input], fiscal_years=years))
            progress.progress(index / max(len(inputs), 1))

        elapsed = elapsed_since(started_at)
        st.session_state["last_extraction_time"] = elapsed
        st.session_state["batch_records"] = records
        st.session_state["latest_records"] = records
        st.session_state["batch_elapsed"] = elapsed
        status.write("Processing complete.")

    records: list[CompanyRecord] = st.session_state.get("batch_records", [])
    if records:
        render_summary(records, st.session_state.get("batch_elapsed"))
        render_results_table(records, key_prefix="batch")
        render_downloads(records, output_dir / "batch")


def _save_upload(uploaded_file: object) -> Path:
    upload_dir = settings.cache_dir / "streamlit_uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    name = getattr(uploaded_file, "name", "upload.csv")
    path = upload_dir / Path(name).name
    path.write_bytes(uploaded_file.getbuffer())
    return path
