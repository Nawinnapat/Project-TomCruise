from __future__ import annotations

from models.company import CompanyInput
from services.extraction_service import ExtractionService


class FakeClient:
    def search_companies(self, keyword):
        return {"contents": [{"jpNo": keyword, "jpTypeCode": "7", "jpName": "ปตท. จำกัด (มหาชน)"}]}

    def company_profile(self, juristic_type, juristic_id):
        assert juristic_type == "7"
        return {
            "jpNo": juristic_id,
            "jpName": "ปตท. จำกัด (มหาชน)",
            "fiscalYear": 2568,
            "jpStatus": {"jpStatDesc": "ยังดำเนินกิจการอยู่"},
        }

    def name_changes(self, juristic_type, juristic_id):
        return []

    def capital_changes(self, juristic_type, juristic_id):
        return []

    def mergers(self, juristic_type, juristic_id):
        return []

    def financial_statements(self, juristic_type, juristic_id, fiscal_year):
        return {
            "basics": {"fiscalYear": int(fiscal_year), "revenueA": 10, "profitlossA": 2},
            "balancesheet": {"finStatementDailyDtos": [{"fiscalYear": int(fiscal_year), "assets": 30, "liabilities": 4}]},
            "profitloss": {"finStatementDailyDtos": [{"fiscalYear": int(fiscal_year), "revenue": 10, "profitloss": 2}]},
            "ratio": {},
            "submit": [],
        }


def test_extract_one_resolves_juristic_type_and_financials_from_profile_year():
    record = ExtractionService(client=FakeClient()).extract_one(CompanyInput(juristic_id="0107544000108"))

    assert record.company_name == "ปตท. จำกัด (มหาชน)"
    assert record.juristic_id == "0107544000108"
    assert record.revenue == 10
    assert record.profit == 2
    assert record.assets == 30
    assert record.liabilities == 4
    assert record.confidence_score == 100
    assert not record.review_required

