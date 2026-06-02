from __future__ import annotations

from pathlib import Path
from time import time
from typing import Any

import streamlit as st

from exporters.csv_exporter import export_csv, export_errors_csv
from exporters.excel_exporter import export_xlsx
from exporters.json_exporter import export_json
from exporters.report_exporter import export_processing_report
from models.company import CompanyRecord


DISPLAY_FIELDS = [
    "company_name",
    "juristic_id",
    "registration_status",
    "registration_date",
    "registered_capital",
    "address",
    "business_type",
    "registration_business_type",
    "registration_business_objective",
    "latest_financial_business_type",
    "latest_financial_business_objective",
    "industry_code",
    "revenue",
    "profit",
    "loss",
    "assets",
    "liabilities",
    "company_size",
    "confidence_score",
    "extraction_timestamp",
]

FIELD_LABELS = {
    "company_name": "Company Name",
    "juristic_id": "Juristic ID",
    "registration_status": "Registration Status",
    "registration_date": "Registration Date",
    "registered_capital": "Registered Capital",
    "address": "Address",
    "business_type": "Business Type",
    "registration_business_type": "Registration Business Type",
    "registration_business_objective": "Registration Business Objective",
    "latest_financial_business_type": "Latest Financial Business Type",
    "latest_financial_business_objective": "Latest Financial Business Objective",
    "industry_code": "Industry Code",
    "revenue": "Revenue",
    "profit": "Profit",
    "loss": "Loss",
    "assets": "Assets",
    "liabilities": "Liabilities",
    "company_size": "Company Size",
    "confidence_score": "Confidence Score",
    "extraction_timestamp": "Extraction Timestamp",
}


def render_page_header(title: str, caption: str | None = None) -> None:
    st.title(title)
    if caption:
        st.caption(caption)


def render_summary(records: list[CompanyRecord], elapsed_seconds: float | None = None) -> None:
    total = len(records)
    failed = sum(1 for record in records if record.errors)
    successful = total - failed
    columns = st.columns(4)
    columns[0].metric("Total Companies", total)
    columns[1].metric("Successful", successful)
    columns[2].metric("Failed", failed)
    columns[3].metric("Processing Time", _format_seconds(elapsed_seconds))


def render_record_table(record: CompanyRecord) -> None:
    rows = [
        {"Field": FIELD_LABELS[field], "Value": _display_value(record.to_dict().get(field))}
        for field in DISPLAY_FIELDS
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    if record.errors:
        st.error("; ".join(record.errors))


def render_results_table(records: list[CompanyRecord], key_prefix: str = "results") -> None:
    if not records:
        st.info("No results to display.")
        return

    rows = [_record_to_display_row(record) for record in records]
    query = st.text_input("Search results", key=f"{key_prefix}_search")
    failed_only = st.checkbox("Show failed only", key=f"{key_prefix}_failed_only")

    filtered = rows
    if query:
        needle = query.casefold()
        filtered = [
            row
            for row in filtered
            if any(needle in str(value or "").casefold() for value in row.values())
        ]
    if failed_only:
        filtered = [row for row in filtered if row.get("errors")]

    sort_field = st.selectbox("Sort by", list(filtered[0].keys()) if filtered else list(rows[0].keys()), key=f"{key_prefix}_sort")
    ascending = st.checkbox("Ascending", value=True, key=f"{key_prefix}_ascending")
    filtered = sorted(filtered, key=lambda row: str(row.get(sort_field) or ""), reverse=not ascending)

    page_size = st.selectbox("Rows per page", [10, 25, 50, 100], index=0, key=f"{key_prefix}_page_size")
    total_pages = max(1, (len(filtered) + page_size - 1) // page_size)
    page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1, key=f"{key_prefix}_page")
    start = (int(page) - 1) * page_size
    st.caption(f"Showing {min(len(filtered), start + 1) if filtered else 0}-{min(len(filtered), start + page_size)} of {len(filtered)} records")
    st.dataframe(filtered[start : start + page_size], use_container_width=True, hide_index=True)


def render_downloads(records: list[CompanyRecord], output_dir: Path) -> None:
    if not records:
        return
    files = export_records(records, output_dir)
    columns = st.columns(3)
    columns[0].download_button("Download XLSX", files["xlsx"].read_bytes(), "results.xlsx")
    columns[1].download_button("Download CSV", files["csv"].read_bytes(), "results.csv", mime="text/csv")
    columns[2].download_button("Download JSON", files["json"].read_bytes(), "results.json", mime="application/json")


def export_records(records: list[CompanyRecord], output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "results.csv"
    xlsx_path = output_dir / "results.xlsx"
    json_path = output_dir / "results.json"
    export_csv(records, csv_path)
    export_xlsx(records, xlsx_path)
    export_json(records, json_path)
    export_errors_csv(records, output_dir / "errors.csv")
    export_processing_report(records, output_dir / "processing_report.json")
    return {"csv": csv_path, "xlsx": xlsx_path, "json": json_path}


def start_timer() -> float:
    return time()


def elapsed_since(started_at: float) -> float:
    return time() - started_at


def _record_to_display_row(record: CompanyRecord) -> dict[str, Any]:
    row = {FIELD_LABELS[field]: _display_value(record.to_dict().get(field)) for field in DISPLAY_FIELDS}
    row["Review Required"] = record.review_required
    row["errors"] = "; ".join(record.errors)
    return row


def _display_value(value: Any) -> Any:
    if value is None or value == "":
        return "NULL"
    if isinstance(value, list | dict):
        return str(value)
    return value


def _format_seconds(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:.1f}s"
