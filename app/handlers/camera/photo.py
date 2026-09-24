from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.services.camera_service import camera_service

logger = logging.getLogger(__name__)


async def photo_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle the /photo command."""

    if update.effective_message is None:
        return

    # Default camera
    facing = "back"

    # Example:
    # /photo front
    # /photo back
    if context.args:
        facing = context.args[0].lower().strip()

    if facing not in {"front", "back"}:
        await update.effective_message.reply_text(
            "Usage:\n"
            "/photo\n"
            "/photo front\n"
            "/photo back"
        )
        return

    try:
        await update.effective_message.reply_text(
            f"Taking {facing} camera photo..."
        )

        photo_path = await camera_service.take_photo(facing)

        with photo_path.open("rb") as photo_file:
            await update.effective_message.reply_photo(
                photo=photo_file,
                caption=f"{facing.capitalize()} camera photo",
            )

    except ValueError as exc:
        logger.warning("Invalid camera request: %s", exc)

        await update.effective_message.reply_text(
            str(exc)
        )

    except Exception:
        logger.exception("Failed to process /photo command")

        await update.effective_message.reply_text(
            "Failed to capture photo. "
            "Check Termux:API and camera permissions."
        )