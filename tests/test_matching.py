from models.company import CompanyInput
from services.matching import best_match, confidence_score
from utils.thai import normalize_company_name


def test_registration_number_exact_match_scores_100():
    score = confidence_score(
        CompanyInput(company_name="อะไรก็ได้", juristic_id="0107542000011"),
        {"juristic_id": "0107542000011", "company_name": "บริษัท ซีพี ออลล์ จำกัด (มหาชน)"},
    )
    assert score == 100


def test_normalized_name_match_scores_80():
    score = confidence_score(
        CompanyInput(company_name="ซีพี ออลล์"),
        {"company_name": "บริษัท ซีพี ออลล์ จำกัด (มหาชน)"},
    )
    assert score == 80


def test_thai_name_normalization_removes_legal_terms_and_spacing():
    assert normalize_company_name("บริษัท  ปตท. จำกัด (มหาชน)") == "ปตท"
    assert normalize_company_name("บมจ. ปตท.") == "ปตท"


def test_best_match_returns_highest_confidence_candidate():
    match, score = best_match(
        CompanyInput(company_name="ปตท"),
        [
            {"juristic_id": "1", "company_name": "บางจาก คอร์ปอเรชั่น จำกัด (มหาชน)"},
            {"juristic_id": "2", "company_name": "บริษัท ปตท. จำกัด (มหาชน)"},
        ],
    )

    assert match == {"juristic_id": "2", "company_name": "บริษัท ปตท. จำกัด (มหาชน)"}
    assert score == 80
