from telegram.ext import Application, CommandHandler

from app.handlers.system.tts import tts_handler


def register_handlers(application: Application) -> None:
    """Register system handlers."""

    application.add_handler(
        CommandHandler("tts", tts_handler)
    )