from __future__ import annotations

import asyncio
import json
import subprocess


async def get_camera_id(facing: str) -> int:
    """
    Find the Termux camera ID by facing direction.

    Args:
        facing: "front" or "back"

    Returns:
        Camera ID as an integer.

    Raises:
        ValueError: If the requested camera is not available.
        RuntimeError: If termux-camera-info fails.
    """

    facing = facing.lower().strip()

    if facing not in {"front", "back"}:
        raise ValueError("Camera must be 'front' or 'back'.")

    try:
        result = await asyncio.to_thread(
            subprocess.run,
            ["termux-camera-info"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "termux-camera-info is not available. "
            "Make sure Termux:API is installed."
        ) from exc

    if result.returncode != 0:
        error = result.stderr.strip() or "Unable to query cameras."
        raise RuntimeError(error)

    try:
        cameras = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Invalid response from termux-camera-info.") from exc

    for camera in cameras:
        if camera.get("facing") == facing:
            return int(camera["id"])

    raise ValueError(f"No {facing} camera was found on this device.")