from parser.dbd_parser import parse_company_record, parse_search_results


def test_parse_search_results_from_result_list():
    payload = {"ResultList": [{"JuristicID": "0107542000011", "JuristicName": "บริษัท ซีพี ออลล์ จำกัด (มหาชน)"}]}
    results = parse_search_results(payload)
    assert results[0]["juristic_id"] == "0107542000011"
    assert results[0]["company_name"] == "บริษัท ซีพี ออลล์ จำกัด (มหาชน)"


def test_parse_company_record_sets_missing_values_null():
    record = parse_company_record({"JuristicID": "0107542000011"}, financials={})
    assert record.juristic_id == "0107542000011"
    assert record.revenue is None


def test_parse_company_record_extracts_profile_and_nested_financial_statement_rows():
    profile = {
        "jpNo": "0107544000108",
        "jpName": "ปตท. จำกัด (มหาชน)",
        "jpStatus": {"jpStatDesc": "ยังดำเนินกิจการอยู่"},
        "regDate": [2001, 10, 1],
        "capAmt": "28,562,996,250",
        "businessType": {"businessTypeDesc": "ผลิต"},
        "submitObjCode": "19201",
        "businessSizeCode": "L",
    }
    financials = {
        "2568": {
            "basics": {"fiscalYear": 2568, "revenueA": 999},
            "balancesheet": {
                "finStatementDailyDtos": [
                    {"fiscalYear": 2567, "assets": 1, "liabilities": 2},
                    {"fiscalYear": 2568, "assets": 1055827157117, "liabilities": 391960560332},
                ]
            },
            "profitloss": {
                "finStatementDailyDtos": [{"fiscalYear": 2568, "revenue": 1562341446477, "profitloss": 57888942601}]
            },
            "ratio": {},
        }
    }

    record = parse_company_record(profile, financials)

    assert record.registration_date == "2001-10-01"
    assert record.registered_capital == 28562996250
    assert record.business_type == "ผลิต"
    assert record.revenue == 1562341446477
    assert record.profit == 57888942601
    assert record.assets == 1055827157117
    assert record.liabilities == 391960560332
