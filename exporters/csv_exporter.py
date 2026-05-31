from __future__ import annotations

import csv
from pathlib import Path

from models.company import CompanyRecord


def export_csv(records: list[CompanyRecord], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [record.to_dict() for record in records]
    fieldnames = list(rows[0].keys()) if rows else list(CompanyRecord().to_dict().keys())
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def export_errors_csv(records: list[CompanyRecord], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["company_name", "juristic_id", "errors", "confidence_score"])
        writer.writeheader()
        for record in records:
            if record.errors or record.review_required:
                writer.writerow(
                    {
                        "company_name": record.company_name,
                        "juristic_id": record.juristic_id,
                        "errors": "; ".join(record.errors),
                        "confidence_score": record.confidence_score,
                    }
                )

