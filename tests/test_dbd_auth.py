from __future__ import annotations

import base64
import json
import time

from scraper.dbd_auth import PlaywrightDbdAuthenticator


def _token(exp: int) -> str:
    payload = base64.urlsafe_b64encode(json.dumps({"exp": exp, "encKey": "abc"}).encode()).rstrip(b"=").decode()
    return f"header.{payload}.sig"


def test_refresh_from_page_returns_id_token():
    token = _token(int(time.time()) + 3600)

    class Page:
        def evaluate(self, script):
            return {"status": 200, "ok": True, "payload": {"idToken": token}, "textKind": "json"}

    assert PlaywrightDbdAuthenticator._refresh_from_page(Page()) == token


def test_refresh_from_page_reports_waf_403():
    class Page:
        def evaluate(self, script):
            return {"status": 403, "ok": False, "payload": None, "textKind": "html/text"}

    try:
        PlaywrightDbdAuthenticator._refresh_from_page(Page())
    except RuntimeError as exc:
        assert "HTTP 403" in str(exc)
    else:
        raise AssertionError("expected WAF failure")
