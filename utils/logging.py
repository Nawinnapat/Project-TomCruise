from __future__ import annotations

import logging
from pathlib import Path

from config.settings import settings


def setup_logging() -> None:
    settings.logs_dir.mkdir(parents=True, exist_ok=True)
    _configure_logger("processing", settings.logs_dir / "processing.log", logging.INFO)
    _configure_logger("validation", settings.logs_dir / "validation.log", logging.INFO)
    _configure_logger("errors", settings.logs_dir / "error.log", logging.ERROR)


def get_logger(name: str) -> logging.Logger:
    setup_logging()
    return logging.getLogger(name)


def _configure_logger(name: str, path: Path, level: int) -> None:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if logger.handlers:
        return
    handler = logging.FileHandler(path, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)

