"""Tests for config.settings module."""

import os
import pytest
from config.settings import Settings


class TestSettings:
    def test_default_values(self):
        settings = Settings()
        assert settings.DOWNLOAD_PATH == "./temp/downloads"
        assert settings.MAX_FILE_SIZE == 2000
        assert settings.MAX_CONCURRENT_DOWNLOADS == 3
        assert settings.LOG_LEVEL == "INFO"

    def test_max_file_size_bytes(self):
        settings = Settings()
        assert settings.max_file_size_bytes == 2000 * 1024 * 1024

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("MAX_FILE_SIZE", "500")
        monkeypatch.setenv("MAX_CONCURRENT_DOWNLOADS", "5")
        settings = Settings()
        assert settings.MAX_FILE_SIZE == 500
        assert settings.MAX_CONCURRENT_DOWNLOADS == 5
