from telegram.ext import Application, CommandHandler

from app.handlers.camera.photo import photo_handler


def register_handlers(application: Application) -> None:
    """Register camera handlers."""

    application.add_handler(
        CommandHandler("photo", photo_handler)
    )