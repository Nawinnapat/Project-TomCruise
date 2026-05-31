from __future__ import annotations

from typing import Any

from scraper.http_client import DbdHttpClient


class DbdDataWarehouseClient:
    def __init__(self, http: DbdHttpClient | None = None) -> None:
        self.http = http or DbdHttpClient()

    def search_companies(self, keyword: str, page: int = 1, page_size: int = 10) -> Any:
        payload = {
            "keyword": keyword,
            "type": "",
            "sortBy": "jpName",
            "currentPage": page,
        }
        if page_size != 10:
            payload["itemsPerPage"] = page_size
        return self.http.post_json("/api/v1/company-profiles/infos", payload)

    def company_profile(self, juristic_type: str, juristic_id: str) -> Any:
        return self.http.get_json(f"/api/v1/company-profiles/info/{juristic_type}/{juristic_id}")

    def committees(self, juristic_type: str, juristic_id: str) -> Any:
        return self.http.get_json(f"/api/v1/company-profiles/committees/{juristic_type}/{juristic_id}")

    def committee_signs(self, juristic_type: str, juristic_id: str) -> Any:
        return self.http.get_json(f"/api/v1/company-profiles/committee-signs/{juristic_type}/{juristic_id}")

    def mergers(self, juristic_type: str, juristic_id: str) -> Any:
        return self.http.get_json(f"/api/v1/company-profiles/mergers/{juristic_type}/{juristic_id}")

    def name_changes(self, juristic_type: str, juristic_id: str) -> Any:
        return self.http.get_json(f"/api/v1/company-profiles/names/{juristic_type}/{juristic_id}")

    def capital_changes(self, juristic_type: str, juristic_id: str) -> Any:
        return self.http.get_json(f"/api/v1/company-profiles/capitals/{juristic_type}/{juristic_id}")

    def balance_sheet(self, juristic_type: str, juristic_id: str, fiscal_year: str) -> Any:
        return self.http.get_json(
            f"/api/v1/fin/balancesheet/year/{juristic_type}/{juristic_id}",
            {"fiscalYear": fiscal_year},
        )

    def profit_loss(self, juristic_type: str, juristic_id: str, fiscal_year: str) -> Any:
        return self.http.get_json(
            f"/api/v1/fin/profitloss/year/{juristic_type}/{juristic_id}",
            {"fiscalYear": fiscal_year},
        )

    def financial_ratios(self, juristic_type: str, juristic_id: str, fiscal_year: str) -> Any:
        return self.http.get_json(
            f"/api/v1/fin/ratio/year/{juristic_type}/{juristic_id}",
            {"fiscalYear": fiscal_year},
        )

    def financial_basics(self, juristic_type: str, juristic_id: str, fiscal_year: str) -> Any:
        return self.http.get_json(
            f"/api/v1/fin/basics/{juristic_type}/{juristic_id}",
            {"fiscalYear": fiscal_year},
        )

    def financial_submit_history(self, juristic_type: str, juristic_id: str, fiscal_year: str) -> Any:
        return self.http.get_json(
            f"/api/v1/fin/submit/{juristic_type}/{juristic_id}",
            {"fiscalYear": fiscal_year},
        )

    def financial_statements(self, juristic_type: str, juristic_id: str, fiscal_year: str) -> dict[str, Any]:
        return {
            "basics": self.financial_basics(juristic_type, juristic_id, fiscal_year),
            "submit": self.financial_submit_history(juristic_type, juristic_id, fiscal_year),
            "balancesheet": self.balance_sheet(juristic_type, juristic_id, fiscal_year),
            "profitloss": self.profit_loss(juristic_type, juristic_id, fiscal_year),
            "ratio": self.financial_ratios(juristic_type, juristic_id, fiscal_year),
        }
