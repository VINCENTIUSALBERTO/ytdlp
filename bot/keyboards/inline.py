"""Inline keyboard builders for the Telegram bot."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def playlist_action_keyboard() -> InlineKeyboardMarkup:
    """Build keyboard for playlist action selection (All / Select / Cancel)."""
    keyboard = [
        [
            InlineKeyboardButton("📥 All Videos", callback_data="action_all"),
            InlineKeyboardButton("🔢 Select Specific", callback_data="action_select"),
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data="action_cancel")],
    ]
    return InlineKeyboardMarkup(keyboard)


def quality_keyboard() -> InlineKeyboardMarkup:
    """Build keyboard for video quality selection."""
    keyboard = [
        [
            InlineKeyboardButton("360p", callback_data="quality_360p"),
            InlineKeyboardButton("480p", callback_data="quality_480p"),
        ],
        [
            InlineKeyboardButton("720p", callback_data="quality_720p"),
            InlineKeyboardButton("1080p", callback_data="quality_1080p"),
        ],
        [
            InlineKeyboardButton("🏆 Best", callback_data="quality_best"),
            InlineKeyboardButton("🎵 Audio (MP3)", callback_data="quality_audio"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def cancel_keyboard() -> InlineKeyboardMarkup:
    """Build a simple cancel keyboard."""
    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="action_cancel")]]
    return InlineKeyboardMarkup(keyboard)
