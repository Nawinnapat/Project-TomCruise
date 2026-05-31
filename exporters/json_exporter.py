from __future__ import annotations

import json
from pathlib import Path

from models.company import CompanyRecord


def export_json(records: list[CompanyRecord], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps([record.to_dict() for record in records], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

