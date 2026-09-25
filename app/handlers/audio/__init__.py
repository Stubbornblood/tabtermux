from telegram.ext import Application, CommandHandler

from app.handlers.audio.record import audio_handler


def register_handlers(application: Application) -> None:
    """Register audio handlers."""

    application.add_handler(
        CommandHandler("audio", audio_handler)
    )