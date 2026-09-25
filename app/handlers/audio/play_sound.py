from __future__ import annotations

import logging
from pathlib import Path
from uuid import uuid4

from telegram import Update
from telegram.ext import ContextTypes

from app.config import settings
from app.services.audio_service import audio_service

logger = logging.getLogger(__name__)


async def play_sound_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Ask the user to send an audio file."""

    if update.effective_message is None:
        return

    context.user_data["awaiting_sound"] = True

    await update.effective_message.reply_text(
        "Send me the sound file you want to play on the tablet."
    )


async def play_sound_file(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Receive an uploaded sound file and play it on the tablet."""

    if update.effective_message is None:
        return

    if not context.user_data.get("awaiting_sound"):
        return

    message = update.effective_message

    telegram_file = None
    original_name = "sound"

    # Normal Telegram audio
    if message.audio:
        telegram_file = await message.audio.get_file()
        original_name = message.audio.file_name or "sound"

    # Telegram document
    elif message.document:
        mime_type = message.document.mime_type or ""

        if (
            not mime_type.startswith("audio/")
            and not _looks_like_audio_file(message.document.file_name)
        ):
            await message.reply_text(
                "Please send an audio file."
            )
            return

        telegram_file = await message.document.get_file()
        original_name = message.document.file_name or "sound"

    # Voice message
    elif message.voice:
        telegram_file = await message.voice.get_file()
        original_name = "voice.ogg"

    else:
        await message.reply_text(
            "Please send an audio file."
        )
        return

    try:
        settings.audio_dir.mkdir(parents=True, exist_ok=True)

        suffix = Path(original_name).suffix or ".audio"
        local_name = f"play_{uuid4().hex}{suffix}"
        local_path = settings.audio_dir / local_name

        await message.reply_text(
            "Downloading sound..."
        )

        await telegram_file.download_to_drive(
            custom_path=local_path
        )

        await audio_service.play_sound(local_path)

        context.user_data["awaiting_sound"] = False

        await message.reply_text(
            f"Playing: {original_name}"
        )

    except Exception:
        logger.exception("Failed to play uploaded sound")

        context.user_data["awaiting_sound"] = False

        await message.reply_text(
            "Failed to play the sound on the tablet."
        )


def _looks_like_audio_file(filename: str | None) -> bool:
    """Check whether a filename has a common audio extension."""

    if not filename:
        return False

    audio_extensions = {
        ".mp3",
        ".wav",
        ".ogg",
        ".oga",
        ".opus",
        ".m4a",
        ".aac",
        ".flac",
        ".amr",
    }

    return Path(filename).suffix.lower() in audio_extensions