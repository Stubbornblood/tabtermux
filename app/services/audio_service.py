from __future__ import annotations

import asyncio
import logging
import subprocess
from datetime import datetime
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)


class AudioService:
    """Handles audio recording and playback through Termux:API."""

    async def record_audio(self, duration: int) -> Path:
        """
        Record audio for the requested number of seconds.
        """

        if duration <= 0:
            raise ValueError("Duration must be greater than 0 seconds.")

        if duration > 300:
            raise ValueError("Maximum recording duration is 300 seconds.")

        settings.audio_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        audio_path = settings.audio_dir / f"audio_{timestamp}.ogg"

        command = [
            "termux-microphone-record",
            "-f",
            str(audio_path),
            "-l",
            str(duration),
            "-e",
            "opus",
        ]

        logger.info(
            "Starting audio recording: duration=%s path=%s",
            duration,
            audio_path,
        )

        try:
            result = await asyncio.to_thread(
                subprocess.run,
                command,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
        except FileNotFoundError as exc:
            raise RuntimeError(
                "termux-microphone-record is not available."
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                "Could not start audio recording."
            ) from exc

        if result.returncode != 0:
            error = result.stderr.strip() or result.stdout.strip()
            raise RuntimeError(
                error or "Failed to start audio recording."
            )

        return audio_path

    async def play_sound(self, file_path: Path) -> None:
        """Play an audio file through the Android device."""

        if not file_path.exists():
            raise FileNotFoundError(
                f"Audio file does not exist: {file_path}"
            )

        command = [
            "termux-media-player",
            "play",
            str(file_path),
        ]

        logger.info("Playing sound: %s", file_path)

        try:
            result = await asyncio.to_thread(
                subprocess.run,
                command,
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
        except FileNotFoundError as exc:
            raise RuntimeError(
                "termux-media-player is not available."
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                "Audio playback command timed out."
            ) from exc

        if result.returncode != 0:
            error = result.stderr.strip() or result.stdout.strip()

            logger.error(
                "Audio playback failed: %s",
                error,
            )

            raise RuntimeError(
                error or "Failed to play audio."
            )


audio_service = AudioService()