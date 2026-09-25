from __future__ import annotations

import asyncio
import logging
import subprocess

logger = logging.getLogger(__name__)


class TTSService:
    """Handles text-to-speech through Termux:API."""

    async def speak(self, text: str) -> None:
        """
        Speak the given text using Termux TTS.

        Args:
            text: Text to speak.

        Raises:
            ValueError: If text is empty.
            RuntimeError: If TTS fails.
        """

        text = text.strip()

        if not text:
            raise ValueError("Text cannot be empty.")

        if len(text) > 500:
            raise ValueError("Text is too long. Maximum length is 500 characters.")

        command = [
            "termux-tts-speak",
            text,
        ]

        logger.info("Speaking text: %s", text)

        try:
            result = await asyncio.to_thread(
                subprocess.run,
                command,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        except FileNotFoundError as exc:
            logger.error("termux-tts-speak not found")
            raise RuntimeError(
                "Termux:API TTS is not available."
            ) from exc
        except subprocess.TimeoutExpired as exc:
            logger.error("TTS command timed out")
            raise RuntimeError(
                "Text-to-speech timed out."
            ) from exc

        if result.returncode != 0:
            error = result.stderr.strip() or result.stdout.strip()

            logger.error(
                "TTS failed: returncode=%s error=%s",
                result.returncode,
                error,
            )

            raise RuntimeError(
                error or "Failed to speak text."
            )


tts_service = TTSService()