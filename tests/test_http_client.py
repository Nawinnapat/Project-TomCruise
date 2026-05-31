from __future__ import annotations

import base64
import json
import time
from typing import Any

from scraper.dbd_auth import DbdAuthState
from scraper.http_client import DbdHttpClient


def _token(exp: int) -> str:
    payload = base64.urlsafe_b64encode(json.dumps({"exp": exp, "encKey": "abc"}).encode()).rstrip(b"=").decode()
    return f"header.{payload}.sig"


def test_refresh_access_token_bootstraps_session_and_sets_authorization(monkeypatch):
    client = DbdHttpClient()
    token = _token(int(time.time()) + 3600)

    class Authenticator:
        def acquire(self):
            return DbdAuthState(
                access_token=token,
                expires_at=int(time.time()) + 3600,
                cookies=[{"name": "visid_incap_2466344", "value": "abc", "domain": ".dbd.go.th", "path": "/"}],
            )

    client.authenticator = Authenticator()

    client._refresh_access_token()

    assert client.access_token == token
    assert client.session.headers["Authorization"] == f"Bearer {token}"
    assert client.session.cookies.get("visid_incap_2466344") == "abc"


def test_request_json_refreshes_after_401(monkeypatch, tmp_path):
    client = DbdHttpClient()
    statuses = [401, 200]
    refreshes = 0

    client.cache.directory = tmp_path
    monkeypatch.setattr(client, "_throttle", lambda: None)

    def refresh() -> None:
        nonlocal refreshes
        refreshes += 1
        client.access_token = _token(int(time.time()) + 3600)
        client.access_token_exp = int(time.time()) + 3600

    def send(method: str, url: str, **kwargs: Any) -> tuple[int, dict[str, object]]:
        return statuses.pop(0), {"ok": True}

    monkeypatch.setattr(client, "_refresh_access_token", lambda force=False: refresh())
    monkeypatch.setattr(client, "_send_json", send)

    assert client.get_json("/api/example") == {"ok": True}
    assert refreshes == 2
    assert statuses == []


def test_bootstrap_session_tolerates_homepage_403():
    client = DbdHttpClient()

    class Response:
        status_code = 403

        def raise_for_status(self):
            raise AssertionError("403 should be tolerated during bootstrap")

    client.session.get = lambda *args, **kwargs: Response()

    client._bootstrap_session()

    assert client._bootstrapped


def test_send_json_fallback_includes_session_cookies(monkeypatch):
    client = DbdHttpClient()
    captured = {}
    client.session.cookies.set("visid_incap_2466344", "abc")
    client.session.cookies.set("incap_ses_392_2466344", "def")

    class Response:
        status_code = 403
        text = "blocked"

        def json(self):
            return {"blocked": True}

    def request(*args, **kwargs):
        return Response()

    def node(method, url, headers, **kwargs):
        captured.update(headers)
        return 200, {"ok": True}

    monkeypatch.setattr(client.session, "request", request)
    monkeypatch.setattr(client, "_send_json_with_node", node)

    status, payload = client._send_json("GET", "https://datawarehouse.dbd.go.th/api/example")

    assert status == 200
    assert payload == {"ok": True}
    assert "visid_incap_2466344=abc" in captured["Cookie"]
    assert "incap_ses_392_2466344=def" in captured["Cookie"]
