#!/usr/bin/env python3
"""Tests for extract_channel_urls.py"""

import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from extract_channel_urls import (
    check_yt_dlp,
    extract_channel_info,
    extract_video_urls,
    save_as_markdown,
)


class TestCheckYtDlp(unittest.TestCase):
    @patch("extract_channel_urls.subprocess.run")
    def test_yt_dlp_installed(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(check_yt_dlp())

    @patch("extract_channel_urls.subprocess.run", side_effect=FileNotFoundError)
    def test_yt_dlp_not_installed(self, mock_run):
        self.assertFalse(check_yt_dlp())

    @patch("extract_channel_urls.subprocess.run")
    def test_yt_dlp_non_zero_return(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1)
        self.assertFalse(check_yt_dlp())


class TestExtractChannelInfo(unittest.TestCase):
    def test_handle_format(self):
        """Falls back to URL parsing when yt-dlp fails."""
        with patch("extract_channel_urls.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="")
            name = extract_channel_info("https://www.youtube.com/@TestChannel")
            self.assertEqual(name, "TestChannel")

    def test_channel_id_format(self):
        with patch("extract_channel_urls.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="")
            name = extract_channel_info("https://www.youtube.com/channel/UC123456")
            self.assertEqual(name, "UC123456")

    def test_custom_url_format(self):
        with patch("extract_channel_urls.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="")
            name = extract_channel_info("https://www.youtube.com/c/MyChannel")
            self.assertEqual(name, "MyChannel")

    def test_yt_dlp_returns_name(self):
        with patch("extract_channel_urls.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="Cool Channel\n", stderr=""
            )
            name = extract_channel_info("https://www.youtube.com/@test")
            self.assertEqual(name, "Cool Channel")

    def test_yt_dlp_strips_videos_suffix(self):
        with patch("extract_channel_urls.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="Cool Channel - Videos\n", stderr=""
            )
            name = extract_channel_info("https://www.youtube.com/@test")
            self.assertEqual(name, "Cool Channel")

    def test_yt_dlp_returns_na(self):
        """When yt-dlp returns NA, falls back to URL parsing."""
        with patch("extract_channel_urls.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="NA\n", stderr=""
            )
            name = extract_channel_info("https://www.youtube.com/@FallbackName")
            self.assertEqual(name, "FallbackName")

    def test_no_match_returns_none(self):
        with patch("extract_channel_urls.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="")
            name = extract_channel_info("https://example.com/something")
            self.assertIsNone(name)


class TestExtractVideoUrls(unittest.TestCase):
    @patch("extract_channel_urls.subprocess.run")
    def test_extracts_full_urls(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="https://www.youtube.com/watch?v=abc\nhttps://www.youtube.com/watch?v=def\n",
            stderr="",
        )
        urls = extract_video_urls("https://www.youtube.com/@test")
        self.assertEqual(len(urls), 2)
        self.assertEqual(urls[0], "https://www.youtube.com/watch?v=abc")
        self.assertEqual(urls[1], "https://www.youtube.com/watch?v=def")

    @patch("extract_channel_urls.subprocess.run")
    def test_extracts_video_ids(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0, stdout="abc123\ndef456\n", stderr=""
        )
        urls = extract_video_urls("https://www.youtube.com/@test")
        self.assertEqual(len(urls), 2)
        self.assertEqual(urls[0], "https://www.youtube.com/watch?v=abc123")
        self.assertEqual(urls[1], "https://www.youtube.com/watch?v=def456")

    @patch("extract_channel_urls.subprocess.run")
    def test_max_videos_flag(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="abc\n", stderr="")
        extract_video_urls("https://www.youtube.com/@test", max_videos=5)
        cmd = mock_run.call_args[0][0]
        self.assertIn("--playlist-end", cmd)
        self.assertIn("5", cmd)

    @patch("extract_channel_urls.subprocess.run")
    def test_error_returns_empty(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")
        urls = extract_video_urls("https://www.youtube.com/@test")
        self.assertEqual(urls, [])

    @patch("extract_channel_urls.subprocess.run")
    def test_timeout_returns_empty(self, mock_run):
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="yt-dlp", timeout=600)
        urls = extract_video_urls("https://www.youtube.com/@test")
        self.assertEqual(urls, [])

    @patch("extract_channel_urls.subprocess.run")
    def test_empty_lines_filtered(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0, stdout="abc\n\n\ndef\n", stderr=""
        )
        urls = extract_video_urls("https://www.youtube.com/@test")
        self.assertEqual(len(urls), 2)


class TestSaveAsMarkdown(unittest.TestCase):
    def test_saves_urls_space_separated(self):
        urls = [
            "https://www.youtube.com/watch?v=abc",
            "https://www.youtube.com/watch?v=def",
        ]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            path = f.name
        try:
            save_as_markdown(urls, "TestChannel", path)
            with open(path, "r") as f:
                content = f.read()
            self.assertEqual(
                content,
                "https://www.youtube.com/watch?v=abc https://www.youtube.com/watch?v=def",
            )
        finally:
            os.unlink(path)

    def test_single_url(self):
        urls = ["https://www.youtube.com/watch?v=abc"]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            path = f.name
        try:
            save_as_markdown(urls, "Test", path)
            with open(path, "r") as f:
                content = f.read()
            self.assertEqual(content, "https://www.youtube.com/watch?v=abc")
        finally:
            os.unlink(path)

    def test_empty_urls(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            path = f.name
        try:
            save_as_markdown([], "Test", path)
            with open(path, "r") as f:
                content = f.read()
            self.assertEqual(content, "")
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
