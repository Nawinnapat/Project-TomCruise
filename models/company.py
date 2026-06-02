from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class CompanyRecord:
    company_name: str | None = None
    juristic_id: str | None = None
    registration_status: str | None = None
    registration_date: str | None = None
    registered_capital: float | None = None
    address: str | None = None
    business_type: str | None = None
    registration_business_type: str | None = None
    registration_business_objective: str | None = None
    latest_financial_business_type: str | None = None
    latest_financial_business_objective: str | None = None
    industry_code: str | None = None
    revenue: float | None = None
    profit: float | None = None
    loss: float | None = None
    assets: float | None = None
    liabilities: float | None = None
    company_size: str | None = None
    historical_changes: list[dict[str, Any]] = field(default_factory=list)
    source_url: str | None = None
    extraction_timestamp: str | None = None
    confidence_score: int = 0
    review_required: bool = True
    raw: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CompanyInput:
    company_name: str | None = None
    juristic_id: str | None = None
