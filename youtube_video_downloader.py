"""
YouTube Video Downloader

This module provides functionality to download individual YouTube videos or
entire playlists using yt-dlp.
"""

import logging
import os
import re
import sys
from typing import Optional
import yt_dlp
from tqdm import tqdm

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Suppress yt-dlp warnings
yt_dlp.utils.bug_reports_message = lambda: ""


def validate_url(url: str) -> bool:
    """
    Checks if the provided URL is a valid YouTube video or playlist URL.

    Args:
        url (str): The URL to validate.

    Returns:
        bool: True if the URL is valid, False otherwise.
    """
    youtube_regex = r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"
    return bool(re.match(youtube_regex, url))


def get_video_info(url: str) -> Optional[dict]:
    """
    Retrieves information about the video or playlist without downloading.

    Args:
        url (str): The URL of the YouTube video or playlist.

    Returns:
        Optional[dict]: Video information if successful, None otherwise.
    """
    ydl_opts = {"quiet": True, "no_warnings": True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)
    except (yt_dlp.DownloadError, yt_dlp.utils.ExtractorError) as e:
        logger.error("Error retrieving video information: %s", str(e))
        return None


def download_youtube_content(
    input_url: str, output_location: str, quality: str = "best"
):
    """
    Downloads YouTube content (video or playlist) to the specified location.

    Args:
        input_url (str): The URL of the YouTube video or playlist.
        output_location (str): The location to save the downloaded content.
        quality (str): The desired video quality ('best', '720', '480', etc.).
    """
    if not validate_url(input_url):
        logger.error("Invalid YouTube URL provided: %s", input_url)
        return

    info = get_video_info(input_url)
    if not info:
        return

    is_playlist = "entries" in info
    content_type = "playlist" if is_playlist else "video"
    logger.info("Preparing to download %s: %s", content_type, info["title"])

    ydl_opts = {
        "format": (
            f"bestvideo[height<={quality}]+bestaudio/best"
            if quality != "best"
            else "best"
        ),
        "outtmpl": os.path.join(output_location, "%(title)s.%(ext)s"),
        "progress_hooks": [progress_hook],
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([input_url])
        logger.info("%s download complete!", content_type.capitalize())
    except yt_dlp.DownloadError as e:
        logger.error("A download error occurred: %s", str(e))
    except yt_dlp.utils.ExtractorError as e:
        logger.error("An extractor error occurred: %s", str(e))
    except OSError as e:
        logger.error("An OS error occurred: %s", str(e))


def progress_hook(d: dict):
    """
    A callback function to log the progress of the download.

    Args:
        d (dict): A dictionary containing download progress information.
    """
    if d["status"] == "downloading":
        total_bytes = d.get("total_bytes")
        downloaded_bytes = d.get("downloaded_bytes", 0)
        if total_bytes:
            progress = (downloaded_bytes / total_bytes) * 100
            filename = os.path.basename(d["filename"])
            tqdm.write(f"Downloading {filename}: {progress:.1f}%", end="\r")
    elif d["status"] == "finished":
        filename = os.path.basename(d["filename"])
        tqdm.write(f"\nFinished downloading {filename}")


def main():
    """Main function to run the YouTube downloader."""
    print("YouTube Video/Playlist Downloader")
    print("=================================")

    user_video_url = input("Enter the YouTube video or playlist URL: ")
    user_storage_location = input("Enter the storage location (absolute path): ")
    user_quality = input("Enter desired quality (e.g., 'best', '720', '480'): ")

    if not os.path.isdir(user_storage_location):
        logger.error("Invalid storage location: %s", user_storage_location)
        return

    download_youtube_content(user_video_url, user_storage_location, user_quality)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDownload cancelled by user.")
        sys.exit(0)
