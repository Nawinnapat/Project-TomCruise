from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from config.settings import settings
from scraper.dbd_crypto import decode_jwt_payload
from utils.logging import get_logger

processing_logger = get_logger("processing")
error_logger = get_logger("errors")


@dataclass(frozen=True)
class DbdAuthState:
    access_token: str
    expires_at: int
    cookies: list[dict[str, Any]]


class PlaywrightDbdAuthenticator:
    def acquire(self) -> DbdAuthState:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:  # pragma: no cover - dependency issue is environment-specific
            raise RuntimeError("Playwright is required for stable DBD authentication") from exc

        workspace_browser_cache = Path("cache/ms-playwright")
        if workspace_browser_cache.exists() and not os.getenv("PLAYWRIGHT_BROWSERS_PATH"):
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(workspace_browser_cache)

        timeout_ms = settings.dbd_playwright_timeout_seconds * 1000
        processing_logger.info("DBD Playwright token acquisition started")
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=settings.dbd_playwright_headless)
            context = browser.new_context(
                user_agent=settings.user_agent,
                locale="th-TH",
                timezone_id="Asia/Bangkok",
                extra_http_headers={
                    "Accept-Language": "th-TH,th;q=0.9,en-US;q=0.8,en;q=0.7",
                },
            )
            page = context.new_page()
            page.set_default_timeout(timeout_ms)
            try:
                page.goto(settings.dbd_base_url, wait_until="domcontentloaded", timeout=timeout_ms)
                page.wait_for_timeout(2500)
                token = self._refresh_from_page(page)
                payload = decode_jwt_payload(token)
                expires_at = int(payload.get("exp") or 0)
                if not expires_at:
                    raise RuntimeError("DBD anonymous JWT did not include exp")
                cookies = context.cookies(settings.dbd_base_url)
                processing_logger.info(
                    "DBD Playwright token acquired exp=%s cookies=%s",
                    expires_at,
                    ",".join(sorted(cookie.get("name", "") for cookie in cookies)),
                )
                return DbdAuthState(access_token=token, expires_at=expires_at, cookies=cookies)
            except Exception as exc:  # noqa: BLE001 - convert all browser auth failures into one boundary error
                error_logger.error("DBD Playwright token acquisition failed error=%s", exc)
                raise
            finally:
                context.close()
                browser.close()

    @staticmethod
    def _refresh_from_page(page: Any) -> str:
        result = page.evaluate(
            """async () => {
                const response = await fetch('/api/refresh', {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Accept': 'application/json, text/plain, */*',
                        'Content-Type': 'application/json'
                    }
                });
                const text = await response.text();
                let payload = null;
                try { payload = JSON.parse(text); } catch {}
                return {
                    status: response.status,
                    ok: response.ok,
                    payload,
                    textKind: text.trim().startsWith('{') ? 'json' : 'html/text'
                };
            }""",
        )
        status = int(result.get("status") or 0)
        payload = result.get("payload") if isinstance(result, dict) else None
        if status >= 400:
            error_logger.error("DBD Playwright refresh returned HTTP %s kind=%s", status, result.get("textKind"))
            raise RuntimeError(f"DBD Playwright refresh failed: HTTP {status}")
        if not isinstance(payload, dict) or not payload.get("idToken"):
            raise RuntimeError("DBD Playwright refresh did not return idToken")
        return str(payload["idToken"])
