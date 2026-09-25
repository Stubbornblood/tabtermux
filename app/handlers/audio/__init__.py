from telegram.ext import Application, CommandHandler, MessageHandler, filters
from app.handlers.audio.record import audio_handler

from app.handlers.audio.play_sound import (
    play_sound_command,
    play_sound_file,
)


def register_handlers(application: Application) -> None:
    """Register audio handlers."""

    application.add_handler(
        CommandHandler("audio", audio_handler)
    )

    application.add_handler(
        CommandHandler("play_sound", play_sound_command)
    )

    application.add_handler(
        MessageHandler(
            filters.AUDIO | filters.VOICE | filters.Document.ALL,
            play_sound_file,
        )
    )