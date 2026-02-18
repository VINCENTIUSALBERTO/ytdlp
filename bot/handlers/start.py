"""Handlers for /start and /help commands."""

from telegram import Update
from telegram.ext import ContextTypes

from database.operations import upsert_user

WELCOME_MESSAGE = (
    "👋 *Welcome to YouTube Playlist Downloader Bot\\!*\n\n"
    "I can download videos from YouTube playlists and send them directly to you\\.\n\n"
    "📌 *How to use:*\n"
    "1\\. Send me a YouTube playlist URL\n"
    "2\\. Choose to download all videos or select specific ones\n"
    "3\\. Pick your preferred quality\n"
    "4\\. I'll download and send the videos to you\\!\n\n"
    "Use /help to see all available commands\\."
)

HELP_MESSAGE = (
    "📖 *Available Commands:*\n\n"
    "/start \\- Welcome message and instructions\n"
    "/help \\- Show this help message\n"
    "/cancel \\- Cancel the current download\n\n"
    "📌 *Usage:*\n"
    "Simply send a YouTube playlist URL and follow the prompts\\.\n\n"
    "🎥 *Supported Formats:*\n"
    "• Video: 360p, 480p, 720p, 1080p, Best\n"
    "• Audio: MP3\n\n"
    "⚠️ *Limitations:*\n"
    "• Max file size: 2 GB per video \\(Telegram limit\\)\n"
    "• Max playlist size: 100 videos\n"
    "• Max concurrent downloads: 3"
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command.

    Sends a welcome message and registers the user in the database.
    """
    if update.effective_user and update.message:
        upsert_user(
            telegram_id=update.effective_user.id,
            username=update.effective_user.username,
            first_name=update.effective_user.first_name,
        )
        await update.message.reply_text(WELCOME_MESSAGE, parse_mode="MarkdownV2")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command.

    Sends a message listing all available commands and usage instructions.
    """
    if update.message:
        await update.message.reply_text(HELP_MESSAGE, parse_mode="MarkdownV2")
