import os
import random
import zipfile
import requests
import platform
import shutil
from urllib.parse import urlparse

from status import *
from config import *

DEFAULT_SONG_ARCHIVE_URLS = []
SAFE_AUDIO_EXTENSIONS = (".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac")


def is_song_archive_url(archive_location: str) -> bool:
    """
    Checks whether a configured songs archive location is a remote URL.

    Args:
        archive_location (str): The configured archive location.

    Returns:
        bool: True if the archive location is an HTTP or HTTPS URL.
    """
    parsed_location = urlparse(archive_location)
    return parsed_location.scheme in ("http", "https")


def resolve_song_archive_path(archive_path: str) -> str:
    """
    Resolves a configured songs archive path.

    Args:
        archive_path (str): An absolute path, or a path relative to the project root.

    Returns:
        str: The resolved path to the archive.
    """
    if os.path.isabs(archive_path):
        return archive_path
    return os.path.join(ROOT_DIR, archive_path)


def extract_songs_archive(archive_path: str, songs_dir: str) -> int:
    """
    Extracts audio files from a songs archive into the Songs directory.

    Args:
        archive_path (str): The path to the zip archive.
        songs_dir (str): The directory to extract songs into.

    Returns:
        int: The number of songs extracted.
    """
    extracted_count = 0

    with zipfile.ZipFile(archive_path, "r") as zf:
        for member in zf.infolist():
            basename = os.path.basename(member.filename)
            if member.is_dir() or not basename:
                continue
            if not basename.lower().endswith(SAFE_AUDIO_EXTENSIONS):
                warning(f"Skipping non-audio file in archive: {member.filename}")
                continue

            destination_path = os.path.join(songs_dir, basename)
            with zf.open(member, "r") as source, open(
                destination_path, "wb"
            ) as destination:
                shutil.copyfileobj(source, destination)
            extracted_count += 1

    return extracted_count


def close_running_selenium_instances() -> None:
    """
    Closes any running Selenium instances.

    Returns:
        None
    """
    try:
        info(" => Closing running Selenium instances...")

        # Kill all running Firefox instances
        if platform.system() == "Windows":
            os.system("taskkill /f /im firefox.exe")
        else:
            os.system("pkill firefox")

        success(" => Closed running Selenium instances.")

    except Exception as e:
        error(f"Error occurred while closing running Selenium instances: {str(e)}")


def build_url(youtube_video_id: str) -> str:
    """
    Builds the URL to the YouTube video.

    Args:
        youtube_video_id (str): The YouTube video ID.

    Returns:
        url (str): The URL to the YouTube video.
    """
    return f"https://www.youtube.com/watch?v={youtube_video_id}"


def rem_temp_files() -> None:
    """
    Removes temporary files in the `.mp` directory.

    Returns:
        None
    """
    # Path to the `.mp` directory
    mp_dir = os.path.join(ROOT_DIR, ".mp")

    files = os.listdir(mp_dir)

    for file in files:
        if not file.endswith(".json"):
            os.remove(os.path.join(mp_dir, file))


def fetch_songs() -> None:
    """
    Extracts songs into Songs/ directory to use with generated videos.

    Returns:
        None
    """
    try:
        info(f" => Fetching songs...")

        files_dir = os.path.join(ROOT_DIR, "Songs")
        configured_archive_path = get_zip_url().strip()
        configured_archive_is_url = is_song_archive_url(configured_archive_path)

        if not os.path.exists(files_dir):
            os.mkdir(files_dir)
            if get_verbose():
                info(f" => Created directory: {files_dir}")
        elif not configured_archive_path or configured_archive_is_url:
            existing_audio_files = [
                name
                for name in os.listdir(files_dir)
                if os.path.isfile(os.path.join(files_dir, name))
                and name.lower().endswith((".mp3", ".wav", ".m4a", ".aac", ".ogg"))
            ]
            if len(existing_audio_files) > 0:
                return

        archive_path = os.path.join(files_dir, "songs.zip")
        extracted = False
        downloaded_archive = False

        resolved_archive_path = ""
        if configured_archive_path and not configured_archive_is_url:
            resolved_archive_path = resolve_song_archive_path(configured_archive_path)

        if resolved_archive_path and os.path.isfile(resolved_archive_path):
            extracted_count = extract_songs_archive(resolved_archive_path, files_dir)
            if extracted_count == 0:
                raise RuntimeError(
                    f"No supported audio files found in archive: {resolved_archive_path}"
                )
            extracted = True
        elif resolved_archive_path:
            raise FileNotFoundError(f"Songs archive not found: {resolved_archive_path}")
        else:
            download_urls = []
            if configured_archive_path:
                download_urls.append(configured_archive_path)
            download_urls.extend(DEFAULT_SONG_ARCHIVE_URLS)

        for download_url in [] if extracted else download_urls:
            try:
                response = requests.get(download_url, timeout=60)
                response.raise_for_status()

                with open(archive_path, "wb") as file:
                    file.write(response.content)
                downloaded_archive = True

                extracted_count = extract_songs_archive(archive_path, files_dir)
                if extracted_count == 0:
                    raise RuntimeError(
                        f"No supported audio files found in archive: {download_url}"
                    )

                extracted = True
                break
            except Exception as err:
                warning(f"Failed to fetch songs from {download_url}: {err}")

        if not extracted:
            raise RuntimeError(
                "Could not extract a valid songs archive from the configured path or URL"
            )

        # Remove only the temporary archive downloaded into Songs/.
        if downloaded_archive and os.path.exists(archive_path):
            os.remove(archive_path)

        success(" => Extracted Songs to ../Songs.")

    except Exception as e:
        error(f"Error occurred while fetching songs: {str(e)}")
        raise


def choose_random_song() -> str:
    """
    Chooses a random song from the songs/ directory.

    Returns:
        str: The path to the chosen song.
    """
    try:
        songs_dir = os.path.join(ROOT_DIR, "Songs")
        songs = [
            name
            for name in os.listdir(songs_dir)
            if os.path.isfile(os.path.join(songs_dir, name))
            and name.lower().endswith(SAFE_AUDIO_EXTENSIONS)
        ]
        if len(songs) == 0:
            raise RuntimeError("No audio files found in Songs directory")
        song = random.choice(songs)
        success(f" => Chose song: {song}")
        return os.path.join(ROOT_DIR, "Songs", song)
    except Exception as e:
        error(f"Error occurred while choosing random song: {str(e)}")
        raise
