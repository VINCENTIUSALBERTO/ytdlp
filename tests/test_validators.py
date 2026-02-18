"""Tests for bot.utils.validators module."""

import pytest
from bot.utils.validators import (
    is_valid_url,
    is_youtube_url,
    is_playlist_url,
    extract_playlist_id,
    sanitize_filename,
)


class TestIsValidUrl:
    def test_valid_http_url(self):
        assert is_valid_url("http://example.com") is True

    def test_valid_https_url(self):
        assert is_valid_url("https://example.com/path") is True

    def test_invalid_scheme(self):
        assert is_valid_url("ftp://example.com") is False

    def test_no_scheme(self):
        assert is_valid_url("example.com") is False

    def test_empty_string(self):
        assert is_valid_url("") is False

    def test_none_input(self):
        assert is_valid_url(None) is False

    def test_random_text(self):
        assert is_valid_url("not a url at all") is False


class TestIsYoutubeUrl:
    def test_youtube_com(self):
        assert is_youtube_url("https://www.youtube.com/watch?v=abc") is True

    def test_youtu_be(self):
        assert is_youtube_url("https://youtu.be/abc") is True

    def test_m_youtube(self):
        assert is_youtube_url("https://m.youtube.com/watch?v=abc") is True

    def test_non_youtube(self):
        assert is_youtube_url("https://vimeo.com/123") is False

    def test_invalid_url(self):
        assert is_youtube_url("not a url") is False


class TestIsPlaylistUrl:
    def test_playlist_url(self):
        url = "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
        assert is_playlist_url(url) is True

    def test_video_with_playlist(self):
        url = "https://www.youtube.com/watch?v=abc&list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
        assert is_playlist_url(url) is True

    def test_video_without_playlist(self):
        url = "https://www.youtube.com/watch?v=abc"
        assert is_playlist_url(url) is False

    def test_non_youtube(self):
        assert is_playlist_url("https://example.com?list=123") is False


class TestExtractPlaylistId:
    def test_extract_id(self):
        url = "https://www.youtube.com/playlist?list=PLrAXtmErZgOei"
        assert extract_playlist_id(url) == "PLrAXtmErZgOei"

    def test_extract_from_video_url(self):
        url = "https://www.youtube.com/watch?v=abc&list=PLtest123"
        assert extract_playlist_id(url) == "PLtest123"

    def test_no_playlist(self):
        url = "https://www.youtube.com/watch?v=abc"
        assert extract_playlist_id(url) is None

    def test_invalid_url(self):
        assert extract_playlist_id("not a url") is None


class TestSanitizeFilename:
    def test_normal_filename(self):
        assert sanitize_filename("video.mp4") == "video.mp4"

    def test_path_traversal(self):
        result = sanitize_filename("../../etc/passwd")
        assert "/" not in result
        assert "\\" not in result

    def test_special_characters(self):
        result = sanitize_filename('video<>:"|?*.mp4')
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result

    def test_long_filename(self):
        long_name = "a" * 250 + ".mp4"
        result = sanitize_filename(long_name)
        assert len(result) <= 204  # 200 + ".mp4"

    def test_empty_after_sanitize(self):
        assert sanitize_filename("...") == "unnamed"

    def test_null_bytes(self):
        result = sanitize_filename("video\0name.mp4")
        assert "\0" not in result
