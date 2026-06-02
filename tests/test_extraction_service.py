from __future__ import annotations

from models.company import CompanyInput
from services.extraction_service import ExtractionService


class FakeClient:
    def search_companies(self, keyword):
        return {
            "contents": [
                {
                    "jpNo": keyword,
                    "jpTypeCode": "7",
                    "jpName": "PTT PUBLIC COMPANY LIMITED",
                    "setupObjCode": "10799",
                    "setupObjType": {"objDesc": "การผลิตผลิตภัณฑ์อาหารอื่น ๆ ซึ่งมิได้จัดประเภทไว้ในที่อื่น"},
                    "setupObjNameKeyin": "ประกอบกิจการผลิตอาหาร เครื่องดื่ม และเครื่องบริโภคอื่นๆ",
                    "submitObjCode": "11043",
                    "submitObjType": {"objDesc": "การผลิตเครื่องดื่มกาแฟ ชาและชาชงสมุนไพรพร้อมดื่ม"},
                    "submitObjNameKeyin": "การผลิตเครื่องดื่มกาแฟ ชาและชาชงสมุนไพรพร้อมดื่ม",
                }
            ]
        }

    def company_profile(self, juristic_type, juristic_id):
        assert juristic_type == "7"
        return {
            "jpNo": juristic_id,
            "jpName": "PTT PUBLIC COMPANY LIMITED",
            "fiscalYear": 2568,
            "jpStatus": {"jpStatDesc": "Operating"},
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

    assert record.company_name == "PTT PUBLIC COMPANY LIMITED"
    assert record.juristic_id == "0107544000108"
    assert record.revenue == 10
    assert record.profit == 2
    assert record.assets == 30
    assert record.liabilities == 4
    assert record.registration_business_type == "10799 การผลิตผลิตภัณฑ์อาหารอื่น ๆ ซึ่งมิได้จัดประเภทไว้ในที่อื่น"
    assert record.registration_business_objective == "ประกอบกิจการผลิตอาหาร เครื่องดื่ม และเครื่องบริโภคอื่นๆ"
    assert record.latest_financial_business_type == "11043 การผลิตเครื่องดื่มกาแฟ ชาและชาชงสมุนไพรพร้อมดื่ม"
    assert record.latest_financial_business_objective == "การผลิตเครื่องดื่มกาแฟ ชาและชาชงสมุนไพรพร้อมดื่ม"
    assert record.confidence_score == 100
    assert not record.review_required
