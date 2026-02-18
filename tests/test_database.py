"""Tests for database models and operations."""

import os
import pytest
from database.models import Base, User, Download
from database.operations import (
    init_db,
    upsert_user,
    record_download,
    update_download_status,
    engine,
    SessionLocal,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    """Use a temporary database for each test."""
    db_path = tmp_path / "test.db"
    db_url = f"sqlite:///{db_path}"

    test_engine = create_engine(db_url, echo=False)
    TestSession = sessionmaker(bind=test_engine)
    Base.metadata.create_all(test_engine)

    # Monkeypatch the module-level engine and session
    import database.operations as ops

    monkeypatch.setattr(ops, "engine", test_engine)
    monkeypatch.setattr(ops, "SessionLocal", TestSession)

    yield TestSession

    test_engine.dispose()


class TestUpsertUser:
    def test_create_new_user(self, setup_test_db):
        upsert_user(telegram_id=12345, username="testuser", first_name="Test")
        session = setup_test_db()
        user = session.query(User).filter_by(telegram_id=12345).first()
        assert user is not None
        assert user.username == "testuser"
        session.close()

    def test_update_existing_user(self, setup_test_db):
        upsert_user(telegram_id=12345, username="old", first_name="Old")
        upsert_user(telegram_id=12345, username="new", first_name="New")
        session = setup_test_db()
        users = session.query(User).filter_by(telegram_id=12345).all()
        assert len(users) == 1
        assert users[0].username == "new"
        session.close()


class TestRecordDownload:
    def test_create_download(self, setup_test_db):
        dl_id = record_download(
            telegram_id=12345,
            video_url="https://youtube.com/watch?v=test",
            video_title="Test Video",
            quality="720p",
        )
        assert dl_id is not None
        session = setup_test_db()
        dl = session.query(Download).filter_by(id=dl_id).first()
        assert dl.video_title == "Test Video"
        assert dl.status == "pending"
        session.close()


class TestUpdateDownloadStatus:
    def test_update_status(self, setup_test_db):
        dl_id = record_download(
            telegram_id=12345,
            video_url="https://youtube.com/watch?v=test",
        )
        update_download_status(dl_id, "completed", file_size=1024)
        session = setup_test_db()
        dl = session.query(Download).filter_by(id=dl_id).first()
        assert dl.status == "completed"
        assert dl.file_size == 1024
        assert dl.completed_at is not None
        session.close()
