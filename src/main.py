from __future__ import annotations

import argparse
from pathlib import Path

from config.settings import settings
from exporters.csv_exporter import export_csv, export_errors_csv
from exporters.excel_exporter import export_xlsx
from exporters.json_exporter import export_json
from exporters.report_exporter import export_processing_report
from models.company import CompanyInput
from services.extraction_service import ExtractionService, load_inputs
from utils.logging import setup_logging


def main() -> None:
    setup_logging()
    parser = argparse.ArgumentParser(description="Extract company data from DBD DataWarehouse")
    parser.add_argument("--input", type=Path, help="CSV/XLSX with company_name and/or juristic_id columns")
    parser.add_argument("--name", help="Single company name")
    parser.add_argument("--juristic-id", help="Single juristic registration number")
    parser.add_argument("--years", default="", help="Comma-separated fiscal years, e.g. 2568,2567,2566")
    parser.add_argument("--output-dir", type=Path, default=settings.output_dir)
    args = parser.parse_args()

    inputs = load_inputs(args.input) if args.input else [CompanyInput(args.name, args.juristic_id)]
    years = [year.strip() for year in args.years.split(",") if year.strip()]
    records = ExtractionService().extract_many(inputs, fiscal_years=years)

    export_csv(records, args.output_dir / "results.csv")
    export_xlsx(records, args.output_dir / "results.xlsx")
    export_json(records, args.output_dir / "results.json")
    export_errors_csv(records, args.output_dir / "errors.csv")
    export_processing_report(records, args.output_dir / "processing_report.json")


if __name__ == "__main__":
    main()

