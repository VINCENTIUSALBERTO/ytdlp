"""Database operations for user and download tracking."""

import datetime
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import aiosqlite
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from config.settings import Settings
from database.models import Base, User, Download

settings = Settings()

# Create synchronous engine (used for table creation)
engine = create_engine(
    settings.DATABASE_URL.replace("sqlite:///", "sqlite:///"),
    echo=False,
)
SessionLocal = sessionmaker(bind=engine)


def init_db() -> None:
    """Create all database tables if they don't exist."""
    Base.metadata.create_all(engine)
    logger.info("Database tables initialized.")


def upsert_user(telegram_id: int, username: str | None, first_name: str | None) -> None:
    """Insert or update a user record.

    Args:
        telegram_id: The Telegram user ID.
        username: The Telegram username.
        first_name: The user's first name.
    """
    with SessionLocal() as session:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if user:
            user.username = username
            user.first_name = first_name
            user.last_active = datetime.datetime.now(datetime.timezone.utc)
        else:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
            )
            session.add(user)
        session.commit()


def record_download(
    telegram_id: int,
    video_url: str,
    video_title: str | None = None,
    quality: str | None = None,
) -> int:
    """Create a new download record and return its ID.

    Args:
        telegram_id: The Telegram user ID.
        video_url: The video URL being downloaded.
        video_title: Title of the video.
        quality: Selected quality setting.

    Returns:
        The ID of the new download record.
    """
    with SessionLocal() as session:
        download = Download(
            telegram_id=telegram_id,
            video_url=video_url,
            video_title=video_title,
            quality=quality,
        )
        session.add(download)
        session.commit()
        return download.id


def update_download_status(
    download_id: int,
    status: str,
    file_size: int | None = None,
) -> None:
    """Update the status of a download record.

    Args:
        download_id: The download record ID.
        status: New status string.
        file_size: Optional file size in bytes.
    """
    with SessionLocal() as session:
        download = session.query(Download).filter_by(id=download_id).first()
        if download:
            download.status = status
            if file_size is not None:
                download.file_size = file_size
            if status in ("completed", "failed"):
                download.completed_at = datetime.datetime.now(datetime.timezone.utc)
            session.commit()
