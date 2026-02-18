"""Main entry point for the Telegram YouTube Playlist Downloader Bot."""

import asyncio
import sys

from loguru import logger
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from config.settings import Settings
from bot.handlers.start import start_command, help_command
from bot.handlers.playlist import handle_url, handle_video_selection
from bot.handlers.download import (
    handle_action_callback,
    handle_quality_callback,
    cancel_command,
)
from bot.utils.file_manager import cleanup_old_files
from database.operations import init_db

settings = Settings()


def setup_logging() -> None:
    """Configure loguru for file and console logging."""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stderr,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>",
    )
    logger.add(
        "logs/bot.log",
        rotation="10 MB",
        retention="7 days",
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
        "{name}:{function}:{line} | {message}",
    )


async def periodic_cleanup(interval_seconds: int = 3600) -> None:
    """Periodically clean up old temporary files.

    Args:
        interval_seconds: How often to run cleanup (default: 1 hour).
    """
    while True:
        await cleanup_old_files(settings.DOWNLOAD_PATH, max_age_hours=1)
        await asyncio.sleep(interval_seconds)


def main() -> None:
    """Set up and run the Telegram bot."""
    setup_logging()

    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set. Check your .env file.")
        sys.exit(1)

    # Initialize database
    init_db()

    logger.info("Starting Telegram YouTube Playlist Downloader Bot...")

    app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("cancel", cancel_command))

    # Callback query handlers for inline keyboard buttons
    app.add_handler(
        CallbackQueryHandler(handle_action_callback, pattern=r"^action_")
    )
    app.add_handler(
        CallbackQueryHandler(handle_quality_callback, pattern=r"^quality_")
    )

    # Message handler for URLs and video selection — processed in order
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url)
    )

    logger.info("Bot is running. Press Ctrl+C to stop.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
