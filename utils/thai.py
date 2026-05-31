from __future__ import annotations

import re
import unicodedata


LEGAL_TERMS = (
    "บริษัทมหาชนจำกัด",
    "บริษัทจำกัด",
    "ห้างหุ้นส่วนจำกัด",
    "ห้างหุ้นส่วนสามัญนิติบุคคล",
    "ห้างหุ้นส่วน",
    "บริษัท",
    "จำกัดมหาชน",
    "จำกัด",
    "มหาชน",
    "บจก.",
    "บมจ.",
    "หจก.",
)


def normalize_company_name(value: str | None) -> str:
    if not value:
        return ""
    text = _normalize_text(value)
    for term in LEGAL_TERMS:
        text = text.replace(_normalize_text(term), " ")
    text = re.sub(r"[()\"'.,]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _normalize_text(value: str) -> str:
    return unicodedata.normalize("NFKC", value).casefold()
