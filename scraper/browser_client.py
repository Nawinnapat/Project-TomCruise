from __future__ import annotations


class PlaywrightFallbackClient:
    def __init__(self) -> None:
        try:
            import playwright.sync_api  # noqa: F401
        except ImportError as exc:
            raise RuntimeError("Playwright fallback requested but playwright is not installed") from exc

    def extract_company(self, *_args: object, **_kwargs: object) -> None:
        raise NotImplementedError("Browser scraping is reserved as last-resort fallback")

