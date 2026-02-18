"""Database models for user and download tracking."""

import datetime
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def _utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


class User(Base):
    """Represents a Telegram user who has interacted with the bot."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    last_active = Column(DateTime, default=_utcnow)

    def __repr__(self) -> str:
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"


class Download(Base):
    """Represents a single video download record."""

    __tablename__ = "downloads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    video_url = Column(String, nullable=False)
    video_title = Column(String, nullable=True)
    quality = Column(String, nullable=True)
    file_size = Column(BigInteger, nullable=True)
    status = Column(String, default="pending")  # pending, downloading, completed, failed
    started_at = Column(DateTime, default=_utcnow)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<Download(id={self.id}, status={self.status})>"
