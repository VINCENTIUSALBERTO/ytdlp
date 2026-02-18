"""Tests for bot.utils.file_manager module."""

import os
import time
import pytest
import asyncio
from pathlib import Path

from bot.utils.file_manager import cleanup_old_files, get_file_size, format_size


class TestFormatSize:
    def test_bytes(self):
        assert format_size(500) == "500 B"

    def test_zero(self):
        assert format_size(0) == "0 B"

    def test_negative(self):
        assert format_size(-1) == "0 B"

    def test_kilobytes(self):
        assert format_size(1024) == "1.0 KB"

    def test_megabytes(self):
        assert format_size(1024 * 1024) == "1.0 MB"

    def test_gigabytes(self):
        assert format_size(1024**3) == "1.0 GB"

    def test_terabytes(self):
        assert format_size(1024**4) == "1.0 TB"

    def test_fractional_mb(self):
        assert format_size(int(1.5 * 1024 * 1024)) == "1.5 MB"


class TestGetFileSize:
    @pytest.mark.asyncio
    async def test_existing_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello world")
        size = await get_file_size(str(f))
        assert size == 11

    @pytest.mark.asyncio
    async def test_nonexistent_file(self):
        size = await get_file_size("/nonexistent/path/file.txt")
        assert size == 0


class TestCleanupOldFiles:
    @pytest.mark.asyncio
    async def test_removes_old_files(self, tmp_path):
        # Create a file and set its modification time to 2 hours ago
        f = tmp_path / "old_file.txt"
        f.write_text("old content")
        old_time = time.time() - 7200  # 2 hours ago
        os.utime(str(f), (old_time, old_time))

        removed = await cleanup_old_files(str(tmp_path), max_age_hours=1)
        assert removed == 1
        assert not f.exists()

    @pytest.mark.asyncio
    async def test_keeps_recent_files(self, tmp_path):
        f = tmp_path / "new_file.txt"
        f.write_text("new content")

        removed = await cleanup_old_files(str(tmp_path), max_age_hours=1)
        assert removed == 0
        assert f.exists()

    @pytest.mark.asyncio
    async def test_nonexistent_directory(self):
        removed = await cleanup_old_files("/nonexistent/dir", max_age_hours=1)
        assert removed == 0
