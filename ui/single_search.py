from __future__ import annotations

from pathlib import Path

import streamlit as st

from models.company import CompanyInput, CompanyRecord
from services.extraction_service import ExtractionService
from ui.dashboard import elapsed_since, render_downloads, render_page_header, render_record_table, start_timer


def render(service: ExtractionService, output_dir: Path) -> None:
    render_page_header("Single Company Search", "Search by company name or juristic ID.")
    company_name = st.text_input("Company Name")
    juristic_id = st.text_input("Juristic ID")
    years_text = st.text_input("Fiscal Years", placeholder="2568,2567")

    if st.button("Extract Company Data", type="primary"):
        if not company_name.strip() and not juristic_id.strip():
            st.warning("Enter a company name or juristic ID.")
            return
        started_at = start_timer()
        years = [year.strip() for year in years_text.split(",") if year.strip()]
        with st.spinner("Extracting company data from DBD..."):
            record = service.extract_one(
                CompanyInput(company_name=company_name.strip() or None, juristic_id=juristic_id.strip() or None),
                fiscal_years=years,
            )
        st.session_state["last_extraction_time"] = elapsed_since(started_at)
        st.session_state["single_record"] = record
        st.session_state["latest_records"] = [record]

    record: CompanyRecord | None = st.session_state.get("single_record")
    if record:
        render_record_table(record)
        render_downloads([record], output_dir / "single")
