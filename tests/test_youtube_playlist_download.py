"""
Unit tests for the YouTube Playlist Downloader module.

This module contains test cases for the main functions in the
youtube_playlist_downloader.py script.
"""

import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os
import youtube_playlist_downloader as ypd


class TestYoutubePlaylistDownloader(unittest.TestCase):
    """Test cases for the YouTube Playlist Downloader functions."""

    def test_create_safe_filename(self):
        """Test the create_safe_filename function."""
        self.assertEqual(ypd.create_safe_filename("Test Playlist"), "Test Playlist")
        self.assertEqual(ypd.create_safe_filename("Test/Playlist"), "Test_Playlist")
        self.assertEqual(ypd.create_safe_filename("Test:Playlist"), "Test_Playlist")

    @patch("youtube_playlist_downloader.yt_dlp.YoutubeDL")
    def test_get_playlist_info_success(self, mock_ytdl):
        """Test successful playlist info retrieval."""
        mock_instance = MagicMock()
        mock_instance.extract_info.return_value = {"title": "Test Playlist"}
        mock_ytdl.return_value.__enter__.return_value = mock_instance

        result = ypd.get_playlist_info("https://www.youtube.com/playlist?list=abc123")
        self.assertEqual(result, {"title": "Test Playlist"})

    @patch("youtube_playlist_downloader.yt_dlp.YoutubeDL")
    def test_get_playlist_info_failure(self, mock_ytdl):
        """Test playlist info retrieval failure."""
        mock_instance = MagicMock()
        mock_instance.extract_info.side_effect = ypd.yt_dlp.utils.ExtractorError(
            "Test error"
        )
        mock_ytdl.return_value.__enter__.return_value = mock_instance

        result = ypd.get_playlist_info("https://www.youtube.com/playlist?list=abc123")
        self.assertIsNone(result)

    @patch("youtube_playlist_downloader.download_videos")
    @patch("youtube_playlist_downloader.get_playlist_info")
    def test_download_playlist(self, mock_get_playlist_info, mock_download_videos):
        """Test the download_playlist function."""
        mock_get_playlist_info.return_value = {
            "title": "Test Playlist",
            "entries": [{"id": "video1"}, {"id": "video2"}],
        }

        with tempfile.TemporaryDirectory() as tmpdirname:
            ypd.download_playlist(
                "https://www.youtube.com/playlist?list=abc123", tmpdirname
            )

        mock_download_videos.assert_called_once_with(
            [{"id": "video1"}, {"id": "video2"}],
            os.path.join(tmpdirname, "Test Playlist"),
        )

    @patch("youtube_playlist_downloader.download_video")
    def test_download_videos(self, mock_download_video):
        """Test the download_videos function."""
        videos = [{"id": "video1"}, {"id": "video2"}]

        with tempfile.TemporaryDirectory() as tmpdirname:
            ypd.download_videos(videos, tmpdirname)

        mock_download_video.assert_any_call({"id": "video1"}, tmpdirname)
        mock_download_video.assert_any_call({"id": "video2"}, tmpdirname)

    @patch("youtube_playlist_downloader.yt_dlp.YoutubeDL")
    def test_download_video_success(self, mock_ytdl):
        """Test successful video download."""
        mock_instance = MagicMock()
        mock_ytdl.return_value.__enter__.return_value = mock_instance

        with tempfile.TemporaryDirectory() as tmpdirname:
            result = ypd.download_video({"id": "abc123"}, tmpdirname)

        self.assertTrue(result)
        mock_instance.download.assert_called_once()

    @patch("youtube_playlist_downloader.yt_dlp.YoutubeDL")
    def test_download_video_failure(self, mock_ytdl):
        """Test video download failure."""
        mock_instance = MagicMock()
        mock_instance.download.side_effect = ypd.yt_dlp.DownloadError("Test error")
        mock_ytdl.return_value.__enter__.return_value = mock_instance

        with tempfile.TemporaryDirectory() as tmpdirname:
            result = ypd.download_video({"id": "abc123"}, tmpdirname)

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
