from __future__ import annotations

import asyncio
import logging
import subprocess
from datetime import datetime
from pathlib import Path

from app.config import settings
from app.handlers.camera.camera_utils import get_camera_id

logger = logging.getLogger(__name__)


class CameraService:
    """Handles camera operations through Termux:API."""

    async def take_photo(self, facing: str = "back") -> Path:
        """
        Capture a photo using the requested camera.

        Args:
            facing: "front" or "back"

        Returns:
            Path to the captured photo.
        """

        camera_id = await get_camera_id(facing)

        settings.photo_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        photo_path = settings.photo_dir / f"photo_{facing}_{timestamp}.jpg"

        command = [
            "termux-camera-photo",
            "-c",
            str(camera_id),
            str(photo_path),
        ]

        logger.info(
            "Taking %s camera photo using camera ID %s",
            facing,
            camera_id,
        )

        try:
            result = await asyncio.to_thread(
                subprocess.run,
                command,
                capture_output=True,
                text=True,
                timeout=settings.command_timeout,
                check=False,
            )

        except subprocess.TimeoutExpired as exc:
            logger.error("Camera command timed out")
            raise RuntimeError("Camera operation timed out.") from exc

        except FileNotFoundError as exc:
            logger.error("termux-camera-photo command not found")
            raise RuntimeError(
                "Termux:API is not installed or termux-camera-photo is unavailable."
            ) from exc

        if result.returncode != 0:
            error = result.stderr.strip() or "Unknown camera error."

            logger.error(
                "Camera command failed. returncode=%s error=%s",
                result.returncode,
                error,
            )

            raise RuntimeError(f"Camera operation failed: {error}")

        if not photo_path.exists():
            raise RuntimeError(
                "Camera command completed, but the photo file was not created."
            )

        if photo_path.stat().st_size == 0:
            raise RuntimeError("Camera created an empty photo file.")

        logger.info("Photo captured successfully: %s", photo_path)

        return photo_path


camera_service = CameraService()