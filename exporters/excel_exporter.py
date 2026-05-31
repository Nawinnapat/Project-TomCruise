from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

from models.company import CompanyRecord


def export_xlsx(records: list[CompanyRecord], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "results"
    rows = [record.to_dict() for record in records]
    headers = list(rows[0].keys()) if rows else list(CompanyRecord().to_dict().keys())
    sheet.append(headers)
    for row in rows:
        sheet.append([_cell_value(row.get(header)) for header in headers])
    workbook.save(path)


def _cell_value(value: object) -> object:
    if isinstance(value, list | dict):
        return str(value)
    return value

