from __future__ import annotations

import logging

from app.bot import create_application
from app.logging_config import setup_logging

logger = logging.getLogger(__name__)


def main() -> None:
    """Start the Telegram bot."""

    setup_logging()

    logger.info("Starting Telegram Android Bot")

    application = create_application()

    logger.info("Bot is starting polling")

    application.run_polling(
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()