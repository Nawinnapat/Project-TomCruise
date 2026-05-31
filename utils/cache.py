from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

from config.settings import settings


class JsonCache:
    def __init__(self, directory: Path | None = None, ttl_seconds: int | None = None) -> None:
        self.directory = directory or settings.cache_dir
        self.ttl_seconds = ttl_seconds or settings.cache_ttl_seconds
        self.directory.mkdir(parents=True, exist_ok=True)

    def get(self, key: str) -> Any | None:
        path = self._path(key)
        if not path.exists():
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        if time.time() - payload["created_at"] > self.ttl_seconds:
            return None
        return payload["data"]

    def set(self, key: str, data: Any) -> None:
        path = self._path(key)
        path.write_text(
            json.dumps({"created_at": time.time(), "data": data}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _path(self, key: str) -> Path:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return self.directory / f"{digest}.json"

