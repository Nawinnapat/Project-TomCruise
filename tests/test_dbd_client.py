from scraper.dbd_client import DbdDataWarehouseClient


class FakeHttp:
    def __init__(self) -> None:
        self.calls = []

    def post_json(self, path, payload):
        self.calls.append(("POST", path, payload))
        return {"contents": []}

    def get_json(self, path, params=None):
        self.calls.append(("GET", path, params))
        return {"ok": path}


def test_search_company_uses_real_infos_endpoint_payload():
    http = FakeHttp()
    client = DbdDataWarehouseClient(http=http)

    assert client.search_companies("0107544000108") == {"contents": []}

    assert http.calls == [
        (
            "POST",
            "/api/v1/company-profiles/infos",
            {"keyword": "0107544000108", "type": "", "sortBy": "jpName", "currentPage": 1},
        )
    ]


def test_financial_statements_calls_all_supported_financial_endpoints():
    http = FakeHttp()
    client = DbdDataWarehouseClient(http=http)

    payload = client.financial_statements("7", "0107544000108", "2568")

    assert set(payload) == {"basics", "submit", "balancesheet", "profitloss", "ratio"}
    assert http.calls == [
        ("GET", "/api/v1/fin/basics/7/0107544000108", {"fiscalYear": "2568"}),
        ("GET", "/api/v1/fin/submit/7/0107544000108", {"fiscalYear": "2568"}),
        ("GET", "/api/v1/fin/balancesheet/year/7/0107544000108", {"fiscalYear": "2568"}),
        ("GET", "/api/v1/fin/profitloss/year/7/0107544000108", {"fiscalYear": "2568"}),
        ("GET", "/api/v1/fin/ratio/year/7/0107544000108", {"fiscalYear": "2568"}),
    ]

