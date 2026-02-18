"""Handler for incoming YouTube playlist URLs."""

from telegram import Update
from telegram.ext import ContextTypes

from loguru import logger

from bot.utils.validators import is_youtube_url, is_playlist_url
from bot.downloader.youtube import get_playlist_info
from bot.keyboards.inline import playlist_action_keyboard


def _format_duration(seconds: int | None) -> str:
    """Format duration in seconds to MM:SS or HH:MM:SS."""
    if seconds is None:
        return "N/A"
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages that may contain YouTube URLs.

    Validates the URL, extracts playlist info, and presents action options.
    """
    if not update.message or not update.message.text:
        return

    url = update.message.text.strip()

    if not is_youtube_url(url):
        await update.message.reply_text(
            "❌ That doesn't look like a valid YouTube URL.\n"
            "Please send a YouTube playlist URL."
        )
        return

    if not is_playlist_url(url):
        await update.message.reply_text(
            "⚠️ This appears to be a single video URL, not a playlist.\n"
            "Please send a URL that contains a playlist.\n\n"
            "💡 Playlist URLs typically contain `list=` parameter."
        )
        return

    # Show a loading message while fetching playlist info
    status_msg = await update.message.reply_text("⏳ Fetching playlist information...")

    try:
        playlist_info = await get_playlist_info(url)
    except ValueError as e:
        await status_msg.edit_text(f"❌ Error: {e}")
        return

    if playlist_info["count"] == 0:
        await status_msg.edit_text(
            "❌ This playlist appears to be empty or inaccessible."
        )
        return

    # Store playlist info in user context for later use
    context.user_data["playlist"] = playlist_info
    context.user_data["playlist_url"] = url

    # Build video list message
    lines = [f"🎵 *{playlist_info['title']}*\n"]
    lines.append(f"Found {playlist_info['count']} video(s):\n")
    for i, video in enumerate(playlist_info["videos"][:20], 1):
        duration = _format_duration(video.get("duration"))
        lines.append(f"{i}. {video['title']} ({duration})")

    if playlist_info["count"] > 20:
        lines.append(f"\n... and {playlist_info['count'] - 20} more videos")

    lines.append("\n📥 Select download option:")
    message_text = "\n".join(lines)

    await status_msg.edit_text(
        message_text,
        reply_markup=playlist_action_keyboard(),
    )


async def show_video_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display the full list of videos in the stored playlist."""
    query = update.callback_query
    if not query:
        return
    await query.answer()

    playlist = context.user_data.get("playlist")
    if not playlist:
        await query.edit_message_text("❌ No playlist loaded. Please send a URL first.")
        return

    lines = [f"🎵 *{playlist['title']}*\n"]
    for i, video in enumerate(playlist["videos"], 1):
        duration = _format_duration(video.get("duration"))
        lines.append(f"{i}. {video['title']} ({duration})")

    lines.append(
        "\n📝 Reply with video numbers separated by commas "
        "(e.g., `1,3,5`) to select specific videos."
    )
    await query.edit_message_text("\n".join(lines))

    # Set a flag so the next text message is treated as video selection
    context.user_data["awaiting_selection"] = True


async def handle_video_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle user's video number selection (e.g., '1,3,5').

    Parses the input and stores selected video indices in user context.
    """
    if not update.message or not update.message.text:
        return

    if not context.user_data.get("awaiting_selection"):
        return

    playlist = context.user_data.get("playlist")
    if not playlist:
        await update.message.reply_text("❌ No playlist loaded. Please send a URL first.")
        return

    text = update.message.text.strip()
    try:
        indices = [int(x.strip()) for x in text.split(",")]
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid input. Please send numbers separated by commas (e.g., 1,3,5)."
        )
        return

    max_index = playlist["count"]
    invalid = [i for i in indices if i < 1 or i > max_index]
    if invalid:
        await update.message.reply_text(
            f"❌ Invalid video numbers: {invalid}. "
            f"Please use numbers between 1 and {max_index}."
        )
        return

    # Store selected indices (convert to 0-based)
    context.user_data["selected_indices"] = [i - 1 for i in indices]
    context.user_data["awaiting_selection"] = False

    from bot.keyboards.inline import quality_keyboard

    await update.message.reply_text(
        f"✅ Selected {len(indices)} video(s). Choose quality:",
        reply_markup=quality_keyboard(),
    )
