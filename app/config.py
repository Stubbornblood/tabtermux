from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


# Project root:
# telegram_android_bot/
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load .env from project root
ENV_FILE = PROJECT_ROOT / ".env"
load_dotenv(ENV_FILE)


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    authorized_user_ids: frozenset[int]

    data_dir: Path
    photo_dir: Path
    video_dir: Path
    audio_dir: Path
    download_dir: Path
    temp_dir: Path

    log_level: str
    command_timeout: int
    max_file_size_mb: int


def _get_required_env(name: str) -> str:
    """Return a required environment variable or raise an error."""
    value = os.getenv(name)

    if not value:
        raise ValueError(f"Required environment variable '{name}' is missing.")

    return value.strip()


def _parse_user_ids(value: str) -> frozenset[int]:
    """Parse comma-separated Telegram user IDs."""
    try:
        user_ids = {
            int(user_id.strip())
            for user_id in value.split(",")
            if user_id.strip()
        }
    except ValueError as exc:
        raise ValueError(
            "AUTHORIZED_USER_IDS must contain only numeric Telegram user IDs."
        ) from exc

    if not user_ids:
        raise ValueError("AUTHORIZED_USER_IDS cannot be empty.")

    return frozenset(user_ids)


def load_settings() -> Settings:
    """Load and validate application configuration."""

    bot_token = _get_required_env("TELEGRAM_BOT_TOKEN")

    authorized_user_ids_raw = _get_required_env("AUTHORIZED_USER_IDS")
    authorized_user_ids = _parse_user_ids(authorized_user_ids_raw)

    data_dir = PROJECT_ROOT / os.getenv("DATA_DIR", "data")
    photo_dir = PROJECT_ROOT / os.getenv("PHOTO_DIR", "data/photos")
    video_dir = PROJECT_ROOT / os.getenv("VIDEO_DIR", "data/videos")
    audio_dir = PROJECT_ROOT / os.getenv("AUDIO_DIR", "data/audio")
    download_dir = PROJECT_ROOT / os.getenv("DOWNLOAD_DIR", "data/downloads")
    temp_dir = PROJECT_ROOT / os.getenv("TEMP_DIR", "data/temp")

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    try:
        command_timeout = int(os.getenv("COMMAND_TIMEOUT", "30"))
        max_file_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", "100"))
    except ValueError as exc:
        raise ValueError(
            "COMMAND_TIMEOUT and MAX_FILE_SIZE_MB must be integers."
        ) from exc

    if command_timeout <= 0:
        raise ValueError("COMMAND_TIMEOUT must be greater than 0.")

    if max_file_size_mb <= 0:
        raise ValueError("MAX_FILE_SIZE_MB must be greater than 0.")

    return Settings(
        telegram_bot_token=bot_token,
        authorized_user_ids=authorized_user_ids,
        data_dir=data_dir,
        photo_dir=photo_dir,
        video_dir=video_dir,
        audio_dir=audio_dir,
        download_dir=download_dir,
        temp_dir=temp_dir,
        log_level=log_level,
        command_timeout=command_timeout,
        max_file_size_mb=max_file_size_mb,
    )


settings = load_settings()