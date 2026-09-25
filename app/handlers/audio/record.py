from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.services.audio_service import audio_service

logger = logging.getLogger(__name__)


async def audio_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle the /audio command."""

    if update.effective_message is None:
        return

    if not context.args:
        await update.effective_message.reply_text(
            "Usage:\n"
            "/audio 5\n"
            "/audio 10"
            "/audio 30"
        )
        return

    if len(context.args) != 1:
        await update.effective_message.reply_text(
            "Usage: /audio <seconds>\n\n"
            "Example:\n"
            "/audio 5"
        )
        return

    try:
        duration = int(context.args[0])
    except ValueError:
        await update.effective_message.reply_text(
            "Duration must be a number.\n\n"
            "Example: /audio 5"
        )
        return

    if duration <= 0:
        await update.effective_message.reply_text(
            "Duration must be greater than 0 seconds."
        )
        return

    try:
        await update.effective_message.reply_text(
            f"Recording audio for {duration} seconds..."
        )

        audio_path = await audio_service.record_audio(duration)

        with audio_path.open("rb") as audio_file:
            await update.effective_message.reply_audio(
                audio=audio_file,
                caption=f"Audio recording ({duration}s)",
            )

    except ValueError as exc:
        await update.effective_message.reply_text(str(exc))

    except Exception:
        logger.exception("Failed to process /audio command")

        await update.effective_message.reply_text(
            "Failed to record audio. "
            "Check microphone permission and Termux:API."
        )