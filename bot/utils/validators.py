"""URL validation utilities for the Telegram YouTube bot."""

import re
from urllib.parse import urlparse, parse_qs


def is_valid_url(url: str) -> bool:
    """Check if a string is a valid URL.

    Args:
        url: The string to validate.

    Returns:
        True if the string is a valid URL, False otherwise.
    """
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except (ValueError, AttributeError):
        return False


def is_youtube_url(url: str) -> bool:
    """Check if a URL is a valid YouTube URL.

    Args:
        url: The URL to validate.

    Returns:
        True if the URL is a YouTube URL, False otherwise.
    """
    if not is_valid_url(url):
        return False
    parsed = urlparse(url)
    youtube_domains = (
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "youtu.be",
        "www.youtu.be",
    )
    return parsed.netloc in youtube_domains


def is_playlist_url(url: str) -> bool:
    """Check if a URL is a YouTube playlist URL.

    Args:
        url: The URL to validate.

    Returns:
        True if the URL contains a playlist ID, False otherwise.
    """
    if not is_youtube_url(url):
        return False
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    return "list" in query_params


def extract_playlist_id(url: str) -> str | None:
    """Extract the playlist ID from a YouTube URL.

    Args:
        url: The YouTube URL.

    Returns:
        The playlist ID or None if not found.
    """
    if not is_youtube_url(url):
        return None
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    playlist_ids = query_params.get("list")
    if playlist_ids:
        return playlist_ids[0]
    return None


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to prevent path traversal and invalid characters.

    Args:
        filename: The original filename.

    Returns:
        A sanitized filename safe for filesystem use.
    """
    # Remove path separators and null bytes
    filename = filename.replace("/", "_").replace("\\", "_").replace("\0", "")
    # Remove other potentially dangerous characters
    filename = re.sub(r'[<>:"|?*]', "_", filename)
    # Remove leading/trailing dots and spaces
    filename = filename.strip(". ")
    # Limit length to 200 characters
    if len(filename) > 200:
        name, _, ext = filename.rpartition(".")
        if ext and len(ext) <= 10:
            filename = name[: 200 - len(ext) - 1] + "." + ext
        else:
            filename = filename[:200]
    return filename or "unnamed"
