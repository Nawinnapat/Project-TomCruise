from __future__ import annotations

import json
import random
import subprocess
import time
from pathlib import Path
from typing import Any

import requests
from requests.utils import dict_from_cookiejar

from config.settings import settings
from scraper.dbd_auth import PlaywrightDbdAuthenticator
from scraper.dbd_crypto import decrypt_envelope, is_encrypted_envelope
from utils.cache import JsonCache
from utils.logging import get_logger

processing_logger = get_logger("processing")
error_logger = get_logger("errors")


class DbdHttpClient:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.cache = JsonCache()
        self.authenticator = PlaywrightDbdAuthenticator()
        self.access_token: str | None = None
        self.access_token_exp: int = 0
        self._bootstrapped = False
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Accept-Language": "th-TH,th;q=0.9,en-US;q=0.8,en;q=0.7",
                "Content-Type": "application/json",
                "Origin": settings.dbd_base_url,
                "User-Agent": settings.user_agent,
                "Referer": f"{settings.dbd_base_url}/",
            }
        )
        if settings.dbd_cookie:
            self.session.headers["Cookie"] = settings.dbd_cookie

    def get_json(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return self._request_json("GET", path, params=params)

    def post_json(self, path: str, payload: dict[str, Any] | None = None) -> Any:
        return self._request_json("POST", path, json=payload)

    def _request_json(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{settings.dbd_base_url.rstrip('/')}/{path.lstrip('/')}"
        api_path = "/" + path.lstrip("/")
        cache_key = f"{method}:{url}:{kwargs}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            processing_logger.info("cache hit %s", url)
            return cached

        last_error: Exception | None = None
        for attempt in range(1, settings.max_retries + 1):
            self._throttle()
            try:
                self._ensure_access_token()
                status, data = self._send_json(method, url, **kwargs)
                if status == 401:
                    error_logger.error("DBD API returned 401; refreshing token through Playwright")
                    self._refresh_access_token(force=True)
                    status, data = self._send_json(method, url, **kwargs)
                if status >= 400:
                    raise RuntimeError(f"HTTP {status}: {data}")
                if is_encrypted_envelope(data):
                    data = decrypt_envelope(data, api_path, self.access_token or "")
                self.cache.set(cache_key, data)
                processing_logger.info("request ok %s %s", method, url)
                return data
            except Exception as exc:  # noqa: BLE001 - continue batch on all request failures
                last_error = exc
                error_logger.error("request failed attempt=%s method=%s url=%s error=%s", attempt, method, url, exc)

        raise RuntimeError(f"DBD endpoint failed after retries: {url}") from last_error

    def _ensure_access_token(self) -> None:
        if self.access_token and time.time() + 60 < self.access_token_exp:
            return
        self._refresh_access_token()

    def _refresh_access_token(self, force: bool = False) -> None:
        if force:
            processing_logger.info("DBD anonymous token refresh requested")
        auth_state = self.authenticator.acquire()
        self.access_token = auth_state.access_token
        self.access_token_exp = auth_state.expires_at
        self.session.headers["Authorization"] = f"Bearer {auth_state.access_token}"
        self.session.cookies.clear()
        for cookie in auth_state.cookies:
            if not cookie.get("name"):
                continue
            self.session.cookies.set(
                cookie.get("name"),
                cookie.get("value"),
                domain=cookie.get("domain"),
                path=cookie.get("path") or "/",
            )
        self._bootstrapped = True
        processing_logger.info("anonymous DBD token refreshed exp=%s", self.access_token_exp)

    def _bootstrap_session(self) -> None:
        if self._bootstrapped:
            return
        url = f"{settings.dbd_base_url.rstrip('/')}/"
        response = self.session.get(url, timeout=settings.request_timeout_seconds)
        if response.status_code != 403:
            response.raise_for_status()
        else:
            processing_logger.info("DBD homepage bootstrap returned 403; continuing with API refresh fallback")
        self._bootstrapped = True
        processing_logger.info("DBD browser session bootstrapped")

    def _send_json(self, method: str, url: str, auth: bool = True, **kwargs: Any) -> tuple[int, Any]:
        headers = dict(self.session.headers)
        cookie_header = self._cookie_header()
        if cookie_header:
            headers["Cookie"] = cookie_header
        if not auth:
            headers.pop("Authorization", None)
        try:
            response = self.session.request(
                method,
                url,
                timeout=settings.request_timeout_seconds,
                headers=headers,
                **kwargs,
            )
            if response.status_code != 403:
                return response.status_code, response.json() if response.text else None
        except Exception as exc:  # noqa: BLE001 - fallback handles WAF/TLS/client differences
            error_logger.info("requests transport failed method=%s url=%s error=%s", method, url, exc)

        return self._send_json_with_node(method, url, headers=headers, **kwargs)

    def _cookie_header(self) -> str:
        cookies = dict_from_cookiejar(self.session.cookies)
        cookie_header = "; ".join(f"{key}={value}" for key, value in cookies.items())
        configured = self.session.headers.get("Cookie")
        if configured and cookie_header:
            return f"{configured}; {cookie_header}"
        return configured or cookie_header

    @staticmethod
    def _send_json_with_node(method: str, url: str, headers: dict[str, str], **kwargs: Any) -> tuple[int, Any]:
        script = Path(__file__).with_name("node_fetch.mjs")
        payload = {
            "method": method,
            "url": url,
            "headers": headers,
            "params": kwargs.get("params"),
        }
        if kwargs.get("json") is not None:
            payload["json"] = kwargs["json"]
        completed = subprocess.run(
            ["node", str(script)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            timeout=settings.request_timeout_seconds + 10,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr or completed.stdout)
        result = json.loads(completed.stdout)
        body = result.get("body") or ""
        try:
            data = json.loads(body) if body else None
        except json.JSONDecodeError:
            data = body
        return int(result.get("status") or 0), data

    @staticmethod
    def _throttle() -> None:
        time.sleep(random.uniform(settings.min_delay_seconds, settings.max_delay_seconds))
