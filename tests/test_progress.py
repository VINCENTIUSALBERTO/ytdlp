"""Tests for bot.downloader.progress module."""

import pytest
from bot.downloader.progress import DownloadProgress, create_progress_hook


class TestDownloadProgress:
    def test_default_values(self):
        p = DownloadProgress()
        assert p.percentage == 0.0
        assert p.speed_str == "N/A"
        assert p.eta_str == "N/A"

    def test_percentage_calculation(self):
        p = DownloadProgress(downloaded_bytes=50, total_bytes=100)
        assert p.percentage == 50.0

    def test_percentage_zero_total(self):
        p = DownloadProgress(downloaded_bytes=50, total_bytes=0)
        assert p.percentage == 0.0

    def test_speed_str_mb(self):
        p = DownloadProgress(speed=2.5 * 1024 * 1024)
        assert "MB/s" in p.speed_str

    def test_speed_str_kb(self):
        p = DownloadProgress(speed=500 * 1024)
        assert "KB/s" in p.speed_str

    def test_speed_str_bytes(self):
        p = DownloadProgress(speed=500)
        assert "B/s" in p.speed_str

    def test_eta_str_format(self):
        p = DownloadProgress(eta=3661)  # 1 hour, 1 minute, 1 second
        assert p.eta_str == "01:01:01"

    def test_format_progress_message(self):
        p = DownloadProgress(
            filename="test_video.mp4",
            downloaded_bytes=50,
            total_bytes=100,
            speed=1024 * 1024,
            eta=60,
        )
        msg = p.format_progress_message(video_index=1, total_videos=5)
        assert "1/5" in msg
        assert "50%" in msg
        assert "test_video.mp4" in msg


class TestCreateProgressHook:
    def test_downloading_status(self):
        p = DownloadProgress()
        hook = create_progress_hook(p)
        hook(
            {
                "status": "downloading",
                "downloaded_bytes": 100,
                "total_bytes": 200,
                "speed": 5000.0,
                "eta": 30,
                "filename": "video.mp4",
            }
        )
        assert p.status == "downloading"
        assert p.downloaded_bytes == 100
        assert p.total_bytes == 200
        assert p.speed == 5000.0
        assert p.eta == 30

    def test_finished_status(self):
        p = DownloadProgress(total_bytes=200)
        hook = create_progress_hook(p)
        hook({"status": "finished"})
        assert p.status == "finished"
        assert p.downloaded_bytes == 200
        assert p.speed == 0.0
        assert p.eta == 0
