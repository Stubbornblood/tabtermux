from __future__ import annotations

import logging

from telegram.ext import Application

from app.config import settings
from app.handlers.camera import register_handlers as register_camera_handlers

logger = logging.getLogger(__name__)


def create_application() -> Application:
    """Create and configure the Telegram bot application."""

    logger.info("Creating Telegram application")

    application = (
        Application.builder()
        .token(settings.telegram_bot_token)
        .build()
    )

    register_camera_handlers(application)

    logger.info("Camera handlers registered")

    return application