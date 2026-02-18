"""Application settings loaded from environment variables."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Configuration settings for the Telegram YouTube bot."""

    def __init__(self) -> None:
        self.TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.DOWNLOAD_PATH: str = os.getenv("DOWNLOAD_PATH", "./temp/downloads")
        self.MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "2000"))  # in MB
        self.MAX_CONCURRENT_DOWNLOADS: int = int(
            os.getenv("MAX_CONCURRENT_DOWNLOADS", "3")
        )
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
        self.DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///bot.db")

        # Ensure download directory exists
        Path(self.DOWNLOAD_PATH).mkdir(parents=True, exist_ok=True)

    @property
    def max_file_size_bytes(self) -> int:
        """Return max file size in bytes."""
        return self.MAX_FILE_SIZE * 1024 * 1024
