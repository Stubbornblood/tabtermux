from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from app.config import settings


def setup_logging() -> None:
    """Configure application-wide logging."""

    settings.data_dir.mkdir(parents=True, exist_ok=True)

    log_dir = settings.data_dir.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "bot.log"

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level)

    # Prevent duplicate handlers if setup_logging() is called more than once.
    if root_logger.handlers:
        root_logger.handlers.clear()

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)