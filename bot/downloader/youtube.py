"""YouTube download functionality using yt-dlp."""

import asyncio
import os
from typing import Callable

import yt_dlp
from loguru import logger

from bot.downloader.progress import DownloadProgress, create_progress_hook
from bot.utils.validators import sanitize_filename
from config.settings import Settings

settings = Settings()

# Quality format mapping for yt-dlp
QUALITY_FORMATS: dict[str, str] = {
    "360p": "best[height<=360]/bestvideo[height<=360]+bestaudio/best",
    "480p": "best[height<=480]/bestvideo[height<=480]+bestaudio/best",
    "720p": "best[height<=720]/bestvideo[height<=720]+bestaudio/best",
    "1080p": "best[height<=1080]/bestvideo[height<=1080]+bestaudio/best",
    "best": "bestvideo+bestaudio/best",
    "audio": "bestaudio/best",
}


def _get_base_ydl_opts() -> dict:
    """Return base yt-dlp options shared across operations."""
    return {
        "no_warnings": True,
        "quiet": True,
        "no_color": True,
        "socket_timeout": 30,
    }


async def get_playlist_info(url: str) -> dict:
    """Extract playlist metadata without downloading.

    Args:
        url: YouTube playlist URL.

    Returns:
        Dictionary with playlist title, entries (list of video info dicts),
        and total count.

    Raises:
        ValueError: If the URL is not a valid playlist or extraction fails.
    """
    ydl_opts = {
        **_get_base_ydl_opts(),
        "extract_flat": True,
        "playlistend": 100,  # Limit to 100 videos for safety
    }

    def _extract() -> dict:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info is None:
                raise ValueError("Could not extract playlist information.")
            return info

    try:
        info = await asyncio.get_event_loop().run_in_executor(None, _extract)
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"Failed to extract playlist info: {e}")
        raise ValueError(f"Could not access playlist: {e}") from e

    entries = info.get("entries", [])
    videos = []
    for entry in entries:
        if entry is not None:
            videos.append(
                {
                    "url": entry.get("url", ""),
                    "title": entry.get("title", "Unknown"),
                    "duration": entry.get("duration"),
                    "id": entry.get("id", ""),
                }
            )

    return {
        "title": info.get("title", "Unknown Playlist"),
        "videos": videos,
        "count": len(videos),
    }


async def get_video_info(url: str) -> dict:
    """Extract single video metadata without downloading.

    Args:
        url: YouTube video URL.

    Returns:
        Dictionary with video title, duration, and estimated file size.

    Raises:
        ValueError: If extraction fails.
    """
    ydl_opts = _get_base_ydl_opts()

    def _extract() -> dict:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info is None:
                raise ValueError("Could not extract video information.")
            return info

    try:
        info = await asyncio.get_event_loop().run_in_executor(None, _extract)
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"Failed to extract video info: {e}")
        raise ValueError(f"Could not access video: {e}") from e

    return {
        "title": info.get("title", "Unknown"),
        "duration": info.get("duration"),
        "filesize_approx": info.get("filesize_approx"),
        "id": info.get("id", ""),
        "url": url,
    }


async def download_video(
    url: str,
    quality: str = "720p",
    progress_callback: Callable[[DownloadProgress], None] | None = None,
    max_retries: int = 3,
) -> str:
    """Download a video and return the path to the downloaded file.

    Args:
        url: YouTube video URL.
        quality: Quality preset key (e.g., '720p', 'best', 'audio').
        progress_callback: Optional callback invoked with progress updates.
        max_retries: Maximum number of retry attempts on failure.

    Returns:
        Absolute path to the downloaded file.

    Raises:
        ValueError: If the download fails after all retries.
    """
    fmt = QUALITY_FORMATS.get(quality, QUALITY_FORMATS["720p"])
    progress = DownloadProgress()

    outtmpl = os.path.join(settings.DOWNLOAD_PATH, "%(title)s.%(ext)s")
    ydl_opts: dict = {
        **_get_base_ydl_opts(),
        "format": fmt,
        "outtmpl": outtmpl,
        "progress_hooks": [create_progress_hook(progress)],
        "merge_output_format": "mp4",
        "restrictfilenames": True,
    }

    if quality == "audio":
        ydl_opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]

    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:

            def _download() -> str:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    if info is None:
                        raise ValueError("Download returned no information.")
                    filename = ydl.prepare_filename(info)
                    # For audio, the extension changes after post-processing
                    if quality == "audio":
                        base, _ = os.path.splitext(filename)
                        filename = base + ".mp3"
                    return filename

            file_path = await asyncio.get_event_loop().run_in_executor(
                None, _download
            )

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Downloaded file not found: {file_path}")

            logger.info(f"Downloaded: {file_path}")
            return file_path

        except Exception as e:
            last_error = e
            logger.warning(
                f"Download attempt {attempt}/{max_retries} failed: {e}"
            )
            if attempt < max_retries:
                await asyncio.sleep(2 * attempt)

    raise ValueError(
        f"Download failed after {max_retries} attempts: {last_error}"
    )
