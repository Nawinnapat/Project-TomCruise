from __future__ import annotations

import csv
import json

from openpyxl import load_workbook

from exporters.csv_exporter import export_csv, export_errors_csv
from exporters.excel_exporter import export_xlsx
from exporters.json_exporter import export_json
from exporters.report_exporter import export_processing_report
from models.company import CompanyRecord


def test_exporters_write_csv_xlsx_json_and_report(tmp_path):
    records = [
        CompanyRecord(
            company_name="PTT PUBLIC COMPANY LIMITED",
            juristic_id="0107544000108",
            registration_business_type="10799 การผลิตผลิตภัณฑ์อาหารอื่น ๆ ซึ่งมิได้จัดประเภทไว้ในที่อื่น",
            registration_business_objective="ประกอบกิจการผลิตอาหาร เครื่องดื่ม และเครื่องบริโภคอื่นๆ",
            latest_financial_business_type="11043 การผลิตเครื่องดื่มกาแฟ ชาและชาชงสมุนไพรพร้อมดื่ม",
            latest_financial_business_objective="การผลิตเครื่องดื่มกาแฟ ชาและชาชงสมุนไพรพร้อมดื่ม",
            revenue=100,
            confidence_score=100,
            review_required=False,
        ),
        CompanyRecord(company_name="Missing Co", errors=["NOT_FOUND"], confidence_score=0),
    ]

    export_csv(records, tmp_path / "results.csv")
    export_errors_csv(records, tmp_path / "errors.csv")
    export_xlsx(records, tmp_path / "results.xlsx")
    export_json(records, tmp_path / "results.json")
    export_processing_report(records, tmp_path / "processing_report.json")

    with (tmp_path / "results.csv").open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    assert rows[0]["juristic_id"] == "0107544000108"
    assert rows[0]["registration_business_type"].startswith("10799 ")

    with (tmp_path / "errors.csv").open(encoding="utf-8-sig", newline="") as file:
        error_rows = list(csv.DictReader(file))
    assert error_rows[0]["errors"] == "NOT_FOUND"

    workbook = load_workbook(tmp_path / "results.xlsx", read_only=True)
    assert workbook.active["A2"].value == "PTT PUBLIC COMPANY LIMITED"

    payload = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert payload[0]["revenue"] == 100
    assert payload[0]["latest_financial_business_objective"] == "การผลิตเครื่องดื่มกาแฟ ชาและชาชงสมุนไพรพร้อมดื่ม"

    report = json.loads((tmp_path / "processing_report.json").read_text(encoding="utf-8"))
    assert report["total"] == 2
    assert report["success"] == 1
    assert report["failed"] == 1
