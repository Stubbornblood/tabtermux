from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.services.tts_service import tts_service

logger = logging.getLogger(__name__)


async def tts_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle the /tts command."""

    if update.effective_message is None:
        return

    if not context.args:
        await update.effective_message.reply_text(
            "Usage:\n"
            "/tts hello\n"
            "/tts Hello from my tablet"
        )
        return

    text = " ".join(context.args)

    try:
        await tts_service.speak(text)

        await update.effective_message.reply_text(
            f"Speaking: {text}"
        )

    except ValueError as exc:
        await update.effective_message.reply_text(str(exc))

    except Exception:
        logger.exception("Failed to process /tts command")

        await update.effective_message.reply_text(
            "Failed to speak the text. "
            "Check Termux:API and TTS availability."
        )