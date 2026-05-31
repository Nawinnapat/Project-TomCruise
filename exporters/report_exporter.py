from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from models.company import CompanyRecord


def export_processing_report(records: list[CompanyRecord], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "total": len(records),
        "success": len([record for record in records if not record.errors]),
        "failed": len([record for record in records if record.errors]),
        "review_required": len([record for record in records if record.review_required]),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

