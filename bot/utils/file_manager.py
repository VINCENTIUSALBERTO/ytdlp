"""File management utilities for temporary download files."""

import os
import time
import asyncio
from pathlib import Path

from loguru import logger


async def cleanup_old_files(directory: str, max_age_hours: int = 1) -> int:
    """Remove files older than the specified age from a directory.

    Args:
        directory: Path to the directory to clean.
        max_age_hours: Maximum age of files in hours before deletion.

    Returns:
        Number of files removed.
    """
    removed = 0
    max_age_seconds = max_age_hours * 3600
    now = time.time()
    dir_path = Path(directory)

    if not dir_path.exists():
        return 0

    for file_path in dir_path.iterdir():
        if file_path.is_file():
            try:
                file_age = now - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    file_path.unlink()
                    removed += 1
                    logger.debug(f"Removed old file: {file_path.name}")
            except OSError as e:
                logger.error(f"Error removing file {file_path}: {e}")

    if removed > 0:
        logger.info(f"Cleaned up {removed} old file(s) from {directory}")
    return removed


async def get_file_size(file_path: str) -> int:
    """Get the size of a file in bytes.

    Args:
        file_path: Path to the file.

    Returns:
        File size in bytes, or 0 if the file doesn't exist.
    """
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0


def format_size(size_bytes: int) -> str:
    """Format bytes into a human-readable string.

    Args:
        size_bytes: Size in bytes.

    Returns:
        Human-readable size string (e.g., '1.5 MB').
    """
    if size_bytes < 0:
        return "0 B"
    units = [("TB", 1024**4), ("GB", 1024**3), ("MB", 1024**2), ("KB", 1024)]
    for unit, threshold in units:
        if size_bytes >= threshold:
            value = size_bytes / threshold
            return f"{value:.1f} {unit}"
    return f"{size_bytes} B"


async def safe_delete(file_path: str) -> bool:
    """Safely delete a file, logging any errors.

    Args:
        file_path: Path to the file to delete.

    Returns:
        True if the file was deleted, False otherwise.
    """
    try:
        path = Path(file_path)
        if path.exists() and path.is_file():
            path.unlink()
            logger.debug(f"Deleted file: {file_path}")
            return True
    except OSError as e:
        logger.error(f"Error deleting file {file_path}: {e}")
    return False
