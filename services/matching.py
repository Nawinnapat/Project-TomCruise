from __future__ import annotations

from models.company import CompanyInput
from utils.thai import normalize_company_name
from utils.validation import valid_juristic_id


def confidence_score(source: CompanyInput, candidate: dict[str, object]) -> int:
    candidate_id = str(candidate.get("juristic_id") or candidate.get("JuristicID") or "")
    candidate_name = str(candidate.get("company_name") or candidate.get("name") or candidate.get("JuristicName") or "")

    if source.juristic_id and valid_juristic_id(source.juristic_id) and source.juristic_id == candidate_id:
        return 100
    if source.company_name and source.company_name.strip() == candidate_name.strip():
        return 95

    source_name = normalize_company_name(source.company_name)
    target_name = normalize_company_name(candidate_name)
    if source_name and source_name == target_name:
        return 80
    if source_name and target_name and (source_name in target_name or target_name in source_name):
        return 60
    return 0


def best_match(source: CompanyInput, candidates: list[dict[str, object]]) -> tuple[dict[str, object] | None, int]:
    scored = [(candidate, confidence_score(source, candidate)) for candidate in candidates]
    if not scored:
        return None, 0
    return max(scored, key=lambda item: item[1])

