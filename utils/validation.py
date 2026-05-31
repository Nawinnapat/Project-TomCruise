from __future__ import annotations

import re
from typing import Any

from utils.logging import get_logger

validation_logger = get_logger("validation")


def valid_juristic_id(value: str | None) -> bool:
    return bool(value and re.fullmatch(r"\d{13}", value))


def parse_number(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, int | float):
        return float(value)
    text = str(value).strip().replace(",", "")
    if text in {"", "-", "NULL", "null"}:
        return None
    try:
        return float(text)
    except ValueError:
        validation_logger.info("Invalid numeric value: %s", value)
        return None


def clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None

