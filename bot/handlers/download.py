"""Handler for download actions and quality selection callbacks."""

import asyncio
import os

from telegram import Update
from telegram.ext import ContextTypes

from loguru import logger

from bot.downloader.youtube import download_video
from bot.downloader.progress import DownloadProgress
from bot.keyboards.inline import quality_keyboard
from bot.utils.file_manager import get_file_size, format_size, safe_delete
from bot.handlers.playlist import show_video_list
from config.settings import Settings
from database.operations import record_download, update_download_status

settings = Settings()


async def handle_action_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle playlist action button callbacks (All / Select / Cancel)."""
    query = update.callback_query
    if not query or not query.data:
        return
    await query.answer()

    action = query.data

    if action == "action_cancel":
        context.user_data.clear()
        await query.edit_message_text("❌ Operation cancelled.")
        return

    playlist = context.user_data.get("playlist")
    if not playlist:
        await query.edit_message_text("❌ No playlist loaded. Please send a URL first.")
        return

    if action == "action_all":
        # Select all videos
        context.user_data["selected_indices"] = list(range(playlist["count"]))
        await query.edit_message_text(
            f"✅ All {playlist['count']} video(s) selected. Choose quality:",
            reply_markup=quality_keyboard(),
        )

    elif action == "action_select":
        await show_video_list(update, context)


async def handle_quality_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle quality selection button callbacks and start downloads."""
    query = update.callback_query
    if not query or not query.data:
        return
    await query.answer()

    quality = query.data.replace("quality_", "")

    playlist = context.user_data.get("playlist")
    selected_indices = context.user_data.get("selected_indices")

    if not playlist or selected_indices is None:
        await query.edit_message_text(
            "❌ No videos selected. Please send a playlist URL first."
        )
        return

    videos = playlist["videos"]
    selected_videos = [videos[i] for i in selected_indices if i < len(videos)]
    total = len(selected_videos)

    if total == 0:
        await query.edit_message_text("❌ No valid videos selected.")
        return

    await query.edit_message_text(
        f"🚀 Starting download of {total} video(s) in {quality} quality..."
    )

    user_id = update.effective_user.id if update.effective_user else 0

    # Download videos with concurrency limit
    semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_DOWNLOADS)
    chat_id = query.message.chat_id if query.message else None
    if not chat_id:
        return

    for i, video in enumerate(selected_videos, 1):
        video_url = video.get("url", "")
        video_title = video.get("title", "Unknown")

        if not video_url:
            # Construct URL from video ID
            video_id = video.get("id", "")
            if video_id:
                video_url = f"https://www.youtube.com/watch?v={video_id}"
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"⚠️ Skipping video {i}/{total}: no URL available.",
                )
                continue

        # Record the download in the database
        download_id = record_download(
            telegram_id=user_id,
            video_url=video_url,
            video_title=video_title,
            quality=quality,
        )

        progress_msg = await context.bot.send_message(
            chat_id=chat_id,
            text=f"📥 Downloading video {i}/{total}: {video_title}",
        )

        async with semaphore:
            file_path = None
            try:
                update_download_status(download_id, "downloading")

                file_path = await download_video(
                    url=video_url,
                    quality=quality,
                )

                file_size = await get_file_size(file_path)

                if file_size > settings.max_file_size_bytes:
                    await progress_msg.edit_text(
                        f"⚠️ Video {i}/{total}: {video_title}\n"
                        f"File size ({format_size(file_size)}) exceeds "
                        f"Telegram's {settings.MAX_FILE_SIZE} MB limit. Skipping."
                    )
                    update_download_status(download_id, "failed", file_size)
                    await safe_delete(file_path)
                    continue

                await progress_msg.edit_text(
                    f"📤 Sending video {i}/{total}: {video_title} "
                    f"({format_size(file_size)})"
                )

                # Send the file to the user
                with open(file_path, "rb") as f:
                    if quality == "audio":
                        await context.bot.send_audio(
                            chat_id=chat_id,
                            audio=f,
                            title=video_title,
                        )
                    else:
                        await context.bot.send_video(
                            chat_id=chat_id,
                            video=f,
                            caption=video_title,
                            supports_streaming=True,
                        )

                update_download_status(download_id, "completed", file_size)
                await progress_msg.edit_text(
                    f"✅ Video {i}/{total}: {video_title} — Sent!"
                )
                logger.info(
                    f"Sent video {i}/{total} to user {user_id}: {video_title}"
                )

            except Exception as e:
                logger.error(
                    f"Error downloading video {i}/{total} ({video_title}): {e}"
                )
                update_download_status(download_id, "failed")
                await progress_msg.edit_text(
                    f"❌ Video {i}/{total}: {video_title}\n"
                    f"Error: {e}"
                )
            finally:
                # Clean up the downloaded file
                if file_path is not None:
                    await safe_delete(file_path)

    # Clear user data after all downloads complete
    context.user_data.clear()
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"🎉 Download session complete! Processed {total} video(s).",
    )


async def cancel_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle the /cancel command to stop the current operation."""
    context.user_data.clear()
    if update.message:
        await update.message.reply_text(
            "❌ Current operation cancelled. Send a new playlist URL to start again."
        )
