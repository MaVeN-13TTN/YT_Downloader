"""
YouTube Playlist Downloader

This module provides functionality to download YouTube playlists using yt-dlp.
It offers concurrent downloads, robust error handling, and configurable options.
"""

import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional
import yt_dlp
from tqdm import tqdm

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Suppress yt-dlp warnings
yt_dlp.utils.bug_reports_message = lambda: ""


class DownloadConfig:
    """Configuration class for download settings."""

    def __init__(self):
        self.max_retries = 5
        self.max_workers = 4
        self.video_format = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        self.output_template = "%(title)s.%(ext)s"


config = DownloadConfig()


def create_safe_filename(filename: str) -> str:
    """
    Create a safe filename by removing or replacing invalid characters.

    Args:
        filename: The original filename.

    Returns:
        A safe version of the filename.
    """
    return "".join(c if c.isalnum() or c in [" ", "-", "_"] else "_" for c in filename)


def download_video(video_info: Dict[str, str], output_path: str) -> bool:
    """
    Download a single video from the playlist.

    Args:
        video_info: Information about the video to download.
        output_path: Path to save the downloaded video.

    Returns:
        True if download was successful, False otherwise.
    """
    ydl_opts = {
        "format": config.video_format,
        "outtmpl": os.path.join(output_path, config.output_template),
        "quiet": True,
        "no_warnings": True,
    }

    for attempt in range(config.max_retries):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                video_url = f"https://www.youtube.com/watch?v={video_info['id']}"
                ydl.download([video_url])
            return True
        except yt_dlp.DownloadError as error:
            logger.warning(
                "Attempt %d failed for %s: %s",
                attempt + 1,
                video_info.get("title", "Unknown video"),
                str(error),
            )

    logger.error(
        "Failed to download %s after %d attempts",
        video_info.get("title", "Unknown video"),
        config.max_retries,
    )
    return False


def get_playlist_info(playlist_url: str) -> Optional[Dict]:
    """
    Retrieve information about the playlist.

    Args:
        playlist_url: URL of the YouTube playlist.

    Returns:
        Dictionary containing playlist information if successful, None otherwise.
    """
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": "in_playlist",
        "force_generic_extractor": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(playlist_url, download=False)
    except yt_dlp.utils.ExtractorError as error:
        logger.error("Failed to extract playlist information: %s", str(error))
    except yt_dlp.utils.YoutubeDLError as error:
        logger.error("A YouTube-DL error occurred: %s", str(error))

    return None


def download_playlist(playlist_url: str, storage_location: str) -> None:
    """
    Download all videos from a YouTube playlist.

    Args:
        playlist_url: URL of the YouTube playlist.
        storage_location: Path to save the downloaded videos.
    """
    playlist_info = get_playlist_info(playlist_url)
    if not playlist_info:
        logger.error("Failed to retrieve playlist information.")
        return

    if "entries" not in playlist_info:
        logger.error("No videos found in the playlist.")
        return

    playlist_title = playlist_info.get("title", "Untitled Playlist")
    safe_playlist_title = create_safe_filename(playlist_title)
    playlist_path = os.path.join(storage_location, safe_playlist_title)

    try:
        os.makedirs(playlist_path, exist_ok=True)
    except OSError as error:
        logger.error("Failed to create directory %s: %s", playlist_path, str(error))
        return

    logger.info("Downloading playlist: %s", playlist_title)
    download_videos(playlist_info["entries"], playlist_path)
    logger.info("Playlist download complete!")


def download_videos(videos: List[Dict[str, str]], output_path: str) -> None:
    """
    Download multiple videos concurrently.

    Args:
        videos: List of video information dictionaries.
        output_path: Path to save the downloaded videos.
    """
    with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
        futures = [
            executor.submit(download_video, video, output_path)
            for video in videos
            if video
        ]

        for future in tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Downloading videos",
            unit="video",
        ):
            future.result()  # This will re-raise any exceptions that occurred


def main() -> None:
    """Main function to run the YouTube playlist downloader."""
    print("YouTube Playlist Downloader")
    print("===========================")

    playlist_url = input("Enter the URL of the YouTube playlist: ").strip()
    download_location = input("Enter the download location: ").strip()

    if not os.path.isdir(download_location):
        logger.error("Invalid download location. Please provide an existing directory.")
        return

    try:
        download_playlist(playlist_url, download_location)
    except KeyboardInterrupt:
        logger.info("Download interrupted by user.")
    except yt_dlp.DownloadError as error:
        logger.error("A download error occurred: %s", str(error))
    except yt_dlp.utils.ExtractorError as error:
        logger.error("An extractor error occurred: %s", str(error))
    except yt_dlp.utils.YoutubeDLError as error:
        logger.error("A YouTube-DL error occurred: %s", str(error))
    except OSError as error:
        logger.error("An OS error occurred: %s", str(error))


if __name__ == "__main__":
    main()
