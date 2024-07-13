"""
Unit tests for the YouTube Video Downloader module.

This module contains test cases for the main functions in the
youtube_video_downloader.py script.
"""

import unittest
from unittest.mock import patch, MagicMock
import tempfile
import sys
import os
import youtube_video_downloader as yvd

# Add the parent directory to the Python path to import the main script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestYoutubeVideoDownloader(unittest.TestCase):
    """Test cases for the YouTube Video Downloader functions."""

    def test_validate_url(self):
        """Test the URL validation function with various inputs."""
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "http://www.youtube.com/playlist?list=PLSbpzW6bgYdHZq8Pp5uohJM9LZA2oIRwh",
        ]
        invalid_urls = [
            "https://www.google.com",
            "not a url",
            "https://www.youtube.com",
        ]

        for url in valid_urls:
            self.assertTrue(yvd.validate_url(url))

        for url in invalid_urls:
            self.assertFalse(yvd.validate_url(url))

    @patch("youtube_video_downloader.yt_dlp.YoutubeDL")
    def test_get_video_info_success(self, mock_ytdl):
        """Test successful video info retrieval."""
        mock_instance = MagicMock()
        mock_instance.extract_info.return_value = {"title": "Test Video"}
        mock_ytdl.return_value.__enter__.return_value = mock_instance

        result = yvd.get_video_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertEqual(result, {"title": "Test Video"})

    @patch("youtube_video_downloader.yt_dlp.YoutubeDL")
    def test_get_video_info_failure(self, mock_ytdl):
        """Test video info retrieval failure."""
        mock_instance = MagicMock()
        mock_instance.extract_info.side_effect = yvd.yt_dlp.DownloadError("Test error")
        mock_ytdl.return_value.__enter__.return_value = mock_instance

        result = yvd.get_video_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertIsNone(result)

    @patch("youtube_video_downloader.get_video_info")
    @patch("youtube_video_downloader.validate_url")
    @patch("youtube_video_downloader.yt_dlp.YoutubeDL")
    def test_download_youtube_content(
        self, mock_ytdl, mock_validate_url, mock_get_video_info
    ):
        """Test the main download function."""
        mock_validate_url.return_value = True
        mock_get_video_info.return_value = {"title": "Test Video"}
        mock_instance = MagicMock()
        mock_ytdl.return_value.__enter__.return_value = mock_instance

        with tempfile.TemporaryDirectory() as tmpdirname:
            yvd.download_youtube_content(
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ", tmpdirname
            )

        mock_instance.download.assert_called_once()

    @patch("youtube_video_downloader.tqdm.write")
    def test_progress_hook(self, mock_write):
        """Test the progress hook function."""
        d = {
            "status": "downloading",
            "filename": "/path/to/file.mp4",
            "total_bytes": 1000,
            "downloaded_bytes": 500,
        }
        yvd.progress_hook(d)
        mock_write.assert_called_with("Downloading file.mp4: 50.0%", end="\r")

        d["status"] = "finished"
        yvd.progress_hook(d)
        mock_write.assert_called_with("\nFinished downloading file.mp4")


if __name__ == "__main__":
    unittest.main()
