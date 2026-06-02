from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    dbd_base_url: str = os.getenv("DBD_BASE_URL", "https://datawarehouse.dbd.go.th")
    request_timeout_seconds: int = int(os.getenv("DBD_REQUEST_TIMEOUT_SECONDS", "20"))
    max_retries: int = int(os.getenv("DBD_MAX_RETRIES", "3"))
    min_delay_seconds: float = float(os.getenv("DBD_MIN_DELAY_SECONDS", "0.8"))
    max_delay_seconds: float = float(os.getenv("DBD_MAX_DELAY_SECONDS", "2.2"))
    cache_ttl_seconds: int = int(os.getenv("DBD_CACHE_TTL_SECONDS", str(24 * 60 * 60)))
    user_agent: str = os.getenv("DBD_USER_AGENT", "")
    dbd_cookie: str = os.getenv("DBD_COOKIE", "")
    dbd_playwright_channel: str = os.getenv("DBD_PLAYWRIGHT_CHANNEL", "chrome")
    dbd_playwright_headless: bool = os.getenv("DBD_PLAYWRIGHT_HEADLESS", "false").lower() in {"1", "true", "yes"}
    dbd_playwright_timeout_seconds: int = int(os.getenv("DBD_PLAYWRIGHT_TIMEOUT_SECONDS", "45"))
    dbd_chrome_profile_dir: Path = Path(os.getenv("DBD_CHROME_PROFILE_DIR", "cache/dbd-chrome-profile"))
    cache_dir: Path = Path(os.getenv("DBD_CACHE_DIR", "cache"))
    logs_dir: Path = Path(os.getenv("DBD_LOGS_DIR", "logs"))
    output_dir: Path = Path(os.getenv("DBD_OUTPUT_DIR", "output"))


settings = Settings()
