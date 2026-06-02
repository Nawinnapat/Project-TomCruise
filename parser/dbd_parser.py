from __future__ import annotations

from datetime import datetime
from typing import Any

from models.company import CompanyRecord
from utils.validation import clean_text, parse_number


def _items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("contents", "data", "items", "results", "ResultList", "resultList"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return [payload]


def parse_search_results(payload: Any) -> list[dict[str, Any]]:
    results = []
    for item in _items(payload):
        results.append(
            {
                "juristic_id": clean_text(_pick(item, "jpNo", "juristicId", "JuristicID", "juristic_id")),
                "juristic_type": clean_text(_pick(item, "jpTypeCode", "juristicType", "JuristicType", "juristic_type")),
                "company_name": clean_text(_pick(item, "jpName", "name", "nameTh", "JuristicName", "JuristicName_TH")),
                "registration_status": clean_text(
                    _pick(item, "jpStatDesc", "status", "JuristicStatus")
                    or _pick_nested(item, ("jpStatus", "jpStatDesc"))
                ),
                "industry_code": clean_text(_pick(item, "submitObjCode", "setupObjCode", "tsicCode", "StandardID")),
                "raw": item,
            }
        )
    return results


def parse_company_record(
    profile: Any,
    financials: dict[str, Any] | None = None,
    history: list[dict[str, Any]] | None = None,
    search_result: dict[str, Any] | None = None,
) -> CompanyRecord:
    item = _items(profile)[0] if _items(profile) else {}
    source_item = _merge_company_sources(item, search_result or {})
    latest_financial = _latest_financial(financials or {})
    record = CompanyRecord(
        company_name=clean_text(_pick(item, "jpName", "name", "nameTh", "JuristicName", "JuristicName_TH")),
        juristic_id=clean_text(_pick(item, "jpNo", "juristicId", "JuristicID", "juristic_id")),
        registration_status=clean_text(
            _pick(item, "jpStatDesc", "status", "JuristicStatus")
            or _pick_nested(item, ("jpStatus", "jpStatDesc"))
        ),
        registration_date=_format_date(_pick(item, "regDate", "registerDate", "RegisterDate")),
        registered_capital=parse_number(_pick(item, "capAmt", "registerCapital", "RegisterCapital")),
        address=clean_text(_pick(item, "address", "FullAddress", "Address")),
        business_type=clean_text(
            _pick_nested(item, ("businessType", "businessTypeDesc"))
            or _pick_nested(item, ("submitObjType", "objDesc"))
            or _pick_nested(item, ("setupObjType", "objDesc"))
            or _pick_string(item, "businessTypeDesc", "Objective", "BusinessType")
        ),
        registration_business_type=_business_classification(
            source_item,
            "setupObjCode",
            ("setupObjType", "objDesc"),
        ),
        registration_business_objective=clean_text(_pick(source_item, "setupObjNameKeyin")),
        latest_financial_business_type=_business_classification(
            source_item,
            "submitObjCode",
            ("submitObjType", "objDesc"),
        ),
        latest_financial_business_objective=clean_text(_pick(source_item, "submitObjNameKeyin")),
        industry_code=clean_text(_pick(item, "submitObjCode", "setupObjCode", "tsicCode", "StandardID")),
        revenue=parse_number(
            _pick(latest_financial, "revenue", "revenueA", "totalIncome", "totalRevenue", "TotalRevenue")
        ),
        profit=parse_number(
            _pick(latest_financial, "profitloss", "profitlossA", "netProfit", "NetProfit", "profit")
        ),
        loss=parse_number(_pick(latest_financial, "loss", "Loss")),
        assets=parse_number(_pick(latest_financial, "assets", "assetsA", "totalAsset", "TotalAsset")),
        liabilities=parse_number(
            _pick(
                latest_financial,
                "liabilities",
                "liabilitiesA",
                "totalLiability",
                "totalLiabilities",
                "TotalLiabilities",
            )
        ),
        company_size=clean_text(_pick(item, "businessSizeCode", "companySize", "BusinessSize", "size")),
        historical_changes=history or [],
        source_url=None,
        extraction_timestamp=datetime.utcnow().isoformat(timespec="seconds") + "Z",
        raw={"profile": profile, "search_result": search_result or {}, "financials": financials or {}, "history": history or []},
    )
    return record


def _pick(source: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if source.get(key) not in (None, ""):
            return source[key]
    return None


def _merge_company_sources(primary: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any]:
    merged = dict(fallback)
    for key, value in primary.items():
        if value not in (None, ""):
            merged[key] = value
    return merged


def _business_classification(source: dict[str, Any], code_key: str, description_path: tuple[str, ...]) -> str | None:
    code = clean_text(_pick(source, code_key))
    description = clean_text(_pick_nested(source, description_path))
    if code and description:
        return f"{code} {description}"
    return description


def _pick_string(source: dict[str, Any], *keys: str) -> str | None:
    value = _pick(source, *keys)
    return value if isinstance(value, str) else None


def _pick_nested(source: dict[str, Any], path: tuple[str, ...]) -> Any:
    value: Any = source
    for key in path:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value if value not in (None, "") else None


def _format_date(value: Any) -> str | None:
    if isinstance(value, list | tuple) and len(value) >= 3:
        return f"{int(value[0]):04d}-{int(value[1]):02d}-{int(value[2]):02d}"
    return clean_text(value)


def _latest_financial(financials: dict[str, Any]) -> dict[str, Any]:
    for year in sorted(financials.keys(), reverse=True):
        value = financials[year]
        if isinstance(value, dict):
            merged = {}
            for section in ("basics", "balancesheet", "profitloss", "ratio"):
                section_items = _financial_items(value.get(section))
                section_items = _prefer_fiscal_year(section_items, year)
                if section_items:
                    merged.update(section_items[0])
            if merged:
                return merged
        items = _items(value)
        items = _prefer_fiscal_year(items, year)
        if items:
            return items[0]
    return {}


def _financial_items(section: Any) -> list[dict[str, Any]]:
    if isinstance(section, dict):
        items = section.get("finStatementDailyDtos")
        if isinstance(items, list):
            return [item for item in items if isinstance(item, dict)]
    return _items(section)


def _prefer_fiscal_year(items: list[dict[str, Any]], year: str) -> list[dict[str, Any]]:
    exact = [item for item in items if str(item.get("fiscalYear") or item.get("submitYear") or "") == str(year)]
    return exact or items
