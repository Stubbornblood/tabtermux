from __future__ import annotations

import asyncio
import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)


class AudioService:
    """Handles audio recording through Termux:API."""

    async def record_audio(self, duration: int) -> Path:
        """
        Record audio for the requested number of seconds.

        Args:
            duration: Recording duration in seconds.

        Returns:
            Path to the recorded audio file.

        Raises:
            ValueError: For an invalid duration.
            RuntimeError: If recording fails.
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
            logger.error("termux-microphone-record not found")
            raise RuntimeError(
                "termux-microphone-record is not available."
            ) from exc
        except subprocess.TimeoutExpired as exc:
            logger.error("Failed to start audio recording")
            raise RuntimeError(
                "Could not start audio recording."
            ) from exc

        if result.returncode != 0:
            error = result.stderr.strip() or result.stdout.strip()

            logger.error(
                "Audio recording failed: returncode=%s error=%s",
                result.returncode,
                error,
            )

            raise RuntimeError(
                error or "Failed to start audio recording."
            )

        # termux-microphone-record starts the Android recorder and
        # returns before the recording has finished.
        await self._wait_for_recording_to_finish(
            duration=duration,
            expected_file=audio_path,
        )

        if not audio_path.exists():
            raise RuntimeError(
                "Recording finished, but the audio file was not created."
            )

        if audio_path.stat().st_size == 0:
            raise RuntimeError("The recorded audio file is empty.")

        logger.info(
            "Audio recording completed: %s (%s bytes)",
            audio_path,
            audio_path.stat().st_size,
        )

        return audio_path

    async def _wait_for_recording_to_finish(
        self,
        duration: int,
        expected_file: Path,
    ) -> None:
        """
        Wait until Termux:API reports that recording has finished.

        A little extra time is allowed for the audio container to
        finalize and close the file.
        """

        timeout = duration + 15
        elapsed = 0

        while elapsed < timeout:
            try:
                result = await asyncio.to_thread(
                    subprocess.run,
                    [
                        "termux-microphone-record",
                        "-i",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
            except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
                raise RuntimeError(
                    "Unable to check audio recording status."
                ) from exc

            if result.returncode == 0 and result.stdout.strip():
                try:
                    info = json.loads(result.stdout)

                    if not info.get("isRecording", False):
                        # Give the recorder a moment to finish writing
                        # the final container metadata.
                        await asyncio.sleep(0.5)

                        if expected_file.exists():
                            return

                except json.JSONDecodeError:
                    logger.warning(
                        "Could not parse recording status: %s",
                        result.stdout,
                    )

            await asyncio.sleep(1)
            elapsed += 1

        raise RuntimeError(
            "Audio recording did not finish within the expected time."
        )


audio_service = AudioService()