# YouTube Downloader

This project provides Python scripts to download YouTube videos and playlists using the `yt-dlp` library. It offers a command-line interface for users to specify the YouTube URL, download location, and other options.

## Features

- Download individual YouTube videos
- Download entire YouTube playlists
- Specify desired video quality
- Concurrent downloading of videos in a playlist
- Robust error handling and retry mechanism

## Technologies Used

- Python 3.x
- yt-dlp library
- tqdm library (for progress tracking)
- unittest (for unit testing)

## Project Structure

```
.
├── README.md
├── requirements.txt
├── youtube_video_downloader.py
├── youtube_playlist_downloader.py
└── tests
    ├── test_youtube_video_downloader.py
    └── test_youtube_playlist_downloader.py
```

- `README.md`: Project overview and instructions (you're reading it now)
- `requirements.txt`: Lists the required Python dependencies
- `youtube_video_downloader.py`: Script to download individual YouTube videos
- `youtube_playlist_downloader.py`: Script to download YouTube playlists
- `tests/`: Directory containing unit tests
  - `test_youtube_video_downloader.py`: Unit tests for the video downloader script
  - `test_youtube_playlist_downloader.py`: Unit tests for the playlist downloader script

## Main Components

1. **YouTube Video Downloader** (`youtube_video_downloader.py`):

   - Validates YouTube video URLs
   - Retrieves video information using `yt-dlp`
   - Downloads the video to the specified location
   - Handles errors and reports download progress

2. **YouTube Playlist Downloader** (`youtube_playlist_downloader.py`):

   - Retrieves playlist information using `yt-dlp`
   - Creates a directory for the playlist
   - Downloads all videos in the playlist concurrently using multiple worker threads
   - Handles errors and reports download progress

3. **Unit Tests**:
   - `test_youtube_video_downloader.py`: Contains test cases for the video downloader script
   - `test_youtube_playlist_downloader.py`: Contains test cases for the playlist downloader script
   - Ensures the reliability and correctness of the downloader scripts

## Building and Running

1. Clone the repository:

   ```
   git clone https://github.com/your-username/youtube-downloader.git
   ```

2. Navigate to the project directory:

   ```
   cd youtube-downloader
   ```

3. Create a virtual environment (optional but recommended):

   ```
   python -m venv venv
   source venv/bin/activate  # For Unix/Linux
   venv\Scripts\activate  # For Windows
   ```

4. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

5. Run the desired downloader script:

   - To download a single video:
     ```
     python youtube_video_downloader.py
     ```
   - To download a playlist:
     ```
     python youtube_playlist_downloader.py
     ```

6. Follow the prompts to enter the YouTube URL, download location, and other options.

7. The downloaded videos will be saved in the specified location.

## Running Tests

To run the unit tests, execute the following command:

```
python -m unittest discover tests
```

This will run all the test files in the `tests/` directory and display the test results.

---

Feel free to contribute to this project by submitting issues or pull requests on the GitHub repository.
