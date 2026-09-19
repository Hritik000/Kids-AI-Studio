"""
Media Asset Downloader Service.
Safely streams and validates remote HTTP/HTTPS images, videos, and audio clips for local FFmpeg processing.
"""

import os
import hashlib
import tempfile
import urllib.parse
import logging
from typing import Optional
import httpx

logger = logging.getLogger("media_downloader")

# Maximum permitted size in bytes (250 MB)
DEFAULT_MAX_BYTES = 250 * 1024 * 1024
DEFAULT_CONNECT_TIMEOUT = 10.0
DEFAULT_READ_TIMEOUT = 60.0

# Supported mime types and extensions mapping
MIME_EXTENSION_MAP = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "video/mp4": ".mp4",
    "video/webm": ".webm",
    "video/quicktime": ".mov",
    "audio/mpeg": ".mp3",
    "audio/mp3": ".mp3",
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
    "audio/aac": ".aac",
    "audio/m4a": ".m4a",
    "audio/mp4": ".m4a",
    "text/plain": ".ass",
    "application/x-subrip": ".srt"
}

ALLOWED_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".webp", ".gif",
    ".mp4", ".webm", ".mov", ".mkv",
    ".mp3", ".wav", ".aac", ".m4a", ".ogg",
    ".srt", ".ass"
}


class DownloaderError(Exception):
    pass


class InvalidURLError(DownloaderError):
    pass


class DownloadSizeExceededError(DownloaderError):
    pass


class PathTraversalError(DownloaderError):
    pass


class MediaDownloader:
    @classmethod
    def get_assets_dir(cls, project_id: str, base_dir: Optional[str] = None) -> str:
        """Constructs and creates the safe assets working directory for a project."""
        base = base_dir or os.path.join(tempfile.gettempdir(), "kidsai_renders")
        assets_dir = os.path.abspath(os.path.join(base, project_id, "assets"))
        os.makedirs(assets_dir, exist_ok=True)
        return assets_dir

    @classmethod
    def is_http_url(cls, path_or_url: str) -> bool:
        """Returns True if input string is an HTTP/HTTPS URL."""
        if not path_or_url or not isinstance(path_or_url, str):
            return False
        parsed = urllib.parse.urlparse(path_or_url)
        return parsed.scheme in ("http", "https")

    @classmethod
    def resolve_extension(cls, url: str, content_type: Optional[str] = None) -> str:
        """Derives a safe file extension from URL or HTTP Content-Type header."""
        parsed = urllib.parse.urlparse(url)
        url_ext = os.path.splitext(parsed.path)[1].lower()
        if url_ext in ALLOWED_EXTENSIONS:
            return url_ext

        if content_type:
            clean_type = content_type.split(";")[0].strip().lower()
            if clean_type in MIME_EXTENSION_MAP:
                return MIME_EXTENSION_MAP[clean_type]

        return ".bin"

    @classmethod
    def download_asset(
        cls,
        url: str,
        project_id: str,
        base_dir: Optional[str] = None,
        max_bytes: int = DEFAULT_MAX_BYTES,
        timeout_seconds: float = DEFAULT_READ_TIMEOUT
    ) -> str:
        """
        Synchronously downloads a remote HTTP/HTTPS asset, streaming chunks to disk.
        Returns the absolute local file path of the downloaded asset.
        """
        if not cls.is_http_url(url):
            raise InvalidURLError(f"Invalid HTTP/HTTPS URL: '{url}'")

        assets_dir = cls.get_assets_dir(project_id, base_dir=base_dir)
        os.makedirs(assets_dir, exist_ok=True)

        # Generate collision-safe filename using SHA256 of URL
        url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]

        logger.info("Downloading remote media asset for project %s (URL host: %s)", project_id, urllib.parse.urlparse(url).netloc)

        try:
            timeout_config = httpx.Timeout(connect=DEFAULT_CONNECT_TIMEOUT, read=timeout_seconds, write=10.0, pool=10.0)
            with httpx.Client(timeout=timeout_config, follow_redirects=True) as client:
                with client.stream("GET", url) as response:
                    if response.status_code < 200 or response.status_code >= 300:
                        raise DownloaderError(f"HTTP request failed with status code {response.status_code} for URL: {url}")

                    content_type = response.headers.get("content-type")
                    content_length = response.headers.get("content-length")
                    if content_length:
                        try:
                            if int(content_length) > max_bytes:
                                raise DownloadSizeExceededError(f"Content-Length ({content_length} bytes) exceeds limit ({max_bytes} bytes)")
                        except ValueError:
                            pass

                    ext = cls.resolve_extension(url, content_type)
                    filename = f"asset_{url_hash}{ext}"
                    target_path = os.path.abspath(os.path.join(assets_dir, filename))

                    # Path Traversal Check
                    if not target_path.startswith(assets_dir + os.sep) and target_path != assets_dir:
                        raise PathTraversalError(f"Path traversal detected for filename '{filename}'")

                    downloaded_bytes = 0
                    with open(target_path, "wb") as f:
                        for chunk in response.iter_bytes(chunk_size=65536):
                            downloaded_bytes += len(chunk)
                            if downloaded_bytes > max_bytes:
                                f.close()
                                if os.path.exists(target_path):
                                    os.remove(target_path)
                                raise DownloadSizeExceededError(f"Downloaded stream exceeded max allowed size of {max_bytes} bytes")
                            f.write(chunk)

                    # Ensure non-executable file permissions (read/write owner, read group/other)
                    os.chmod(target_path, 0o644)

                    if downloaded_bytes == 0:
                        if os.path.exists(target_path):
                            os.remove(target_path)
                        raise DownloaderError(f"Downloaded asset file is empty (0 bytes) for URL: {url}")

                    logger.info("Successfully downloaded asset %s (%d bytes)", target_path, downloaded_bytes)
                    return target_path

        except Exception as e:
            if isinstance(e, DownloaderError):
                raise e
            raise DownloaderError(f"Failed to download remote asset from {url}: {str(e)}") from e

    @classmethod
    def prepare_media_path(cls, path_or_url: Optional[str], project_id: str, base_dir: Optional[str] = None) -> Optional[str]:
        """
        Helper that passes local file paths through directly, or downloads remote HTTP URLs
        to local disk and returns the local file path.
        """
        if not path_or_url:
            return None

        if cls.is_http_url(path_or_url):
            return cls.download_asset(url=path_or_url, project_id=project_id, base_dir=base_dir)

        abs_path = os.path.abspath(path_or_url)
        if os.path.exists(abs_path):
            return abs_path

        return path_or_url
