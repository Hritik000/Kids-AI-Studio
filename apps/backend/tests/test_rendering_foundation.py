"""
Comprehensive Unit Tests for Rendering Foundation & Media Downloader.
Covers:
1. FFmpeg path discovery
2. Local image input
3. Local audio input
4. HTTP image download
5. HTTP audio download
6. HTTP video download
7. Failed download handling
8. Unsupported URL scheme
9. Missing FFmpeg error handling
10. Path traversal protection
11. Render failure propagation
"""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from app.services.rendering.ffmpeg import FFmpegEngine, FFmpegNotFoundError
from app.services.rendering.downloader import (
    MediaDownloader, DownloaderError, InvalidURLError, DownloadSizeExceededError, PathTraversalError
)
from app.services.rendering.models import RenderJobInput, SceneInput, CameraDirection, TransitionType
from app.services.rendering.renderer import FFmpegRenderer


def test_ffmpeg_path_discovery(monkeypatch):
    """1. Test FFmpeg path discovery via FFMPEG_PATH env var, system PATH, and fallback."""
    # Reset cached binary
    FFmpegEngine._cached_exe = None

    # Test FFMPEG_PATH override
    with tempfile.NamedTemporaryFile(suffix="ffmpeg", delete=False) as f:
        fake_ffmpeg = f.name
    os.chmod(fake_ffmpeg, 0o755)

    try:
        monkeypatch.setenv("FFMPEG_PATH", fake_ffmpeg)
        found_path = FFmpegEngine.get_ffmpeg_path()
        assert found_path == fake_ffmpeg
    finally:
        if os.path.exists(fake_ffmpeg):
            os.remove(fake_ffmpeg)

    # Test missing FFmpeg error
    FFmpegEngine._cached_exe = None
    monkeypatch.delenv("FFMPEG_PATH", raising=False)
    with patch("shutil.which", return_value=None), \
         patch.dict("sys.modules", {"imageio_ffmpeg": None}), \
         patch("os.path.isfile", return_value=False):
        with pytest.raises(FFmpegNotFoundError) as exc_info:
            FFmpegEngine.get_ffmpeg_path()
        assert "FFmpeg executable not found" in str(exc_info.value)


def test_local_image_input():
    """2. Test local image input preparation passes through directly."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        img_path = f.name
        f.write(b"PNG_HEADER_DATA")

    try:
        result = MediaDownloader.prepare_media_path(img_path, project_id="proj_test")
        assert result == os.path.abspath(img_path)
    finally:
        if os.path.exists(img_path):
            os.remove(img_path)


def test_local_audio_input():
    """3. Test local audio input preparation passes through directly."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        aud_path = f.name
        f.write(b"RIFF_WAV_HEADER")

    try:
        result = MediaDownloader.prepare_media_path(aud_path, project_id="proj_test")
        assert result == os.path.abspath(aud_path)
    finally:
        if os.path.exists(aud_path):
            os.remove(aud_path)


def test_http_image_download():
    """4. Test downloading a remote HTTP image with mocked stream response."""
    fake_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"

    def mock_stream(method, url):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {"content-type": "image/png", "content-length": str(len(fake_png))}
        mock_resp.iter_bytes = MagicMock(return_value=[fake_png])
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_resp
        return mock_context

    with patch("httpx.Client.stream", side_effect=mock_stream):
        dl_path = MediaDownloader.download_asset("https://example.com/test_hero.png", project_id="proj_test_img")
        assert os.path.exists(dl_path)
        assert dl_path.endswith(".png")
        with open(dl_path, "rb") as f:
            content = f.read()
        assert content == fake_png
        if os.path.exists(dl_path):
            os.remove(dl_path)


def test_http_audio_download():
    """5. Test downloading a remote HTTP audio file with mocked stream response."""
    fake_mp3 = b"ID3_TAG_DATA_FOR_TESTING_AUDIO"

    def mock_stream(method, url):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {"content-type": "audio/mpeg", "content-length": str(len(fake_mp3))}
        mock_resp.iter_bytes = MagicMock(return_value=[fake_mp3])
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_resp
        return mock_context

    with patch("httpx.Client.stream", side_effect=mock_stream):
        dl_path = MediaDownloader.download_asset("https://example.com/narration.mp3", project_id="proj_test_aud")
        assert os.path.exists(dl_path)
        assert dl_path.endswith(".mp3")
        with open(dl_path, "rb") as f:
            content = f.read()
        assert content == fake_mp3
        if os.path.exists(dl_path):
            os.remove(dl_path)


def test_http_video_download():
    """6. Test downloading a remote HTTP video file with mocked stream response."""
    fake_mp4 = b"\x00\x00\x00\x18ftypmp42"

    def mock_stream(method, url):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {"content-type": "video/mp4", "content-length": str(len(fake_mp4))}
        mock_resp.iter_bytes = MagicMock(return_value=[fake_mp4])
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_resp
        return mock_context

    with patch("httpx.Client.stream", side_effect=mock_stream):
        dl_path = MediaDownloader.download_asset("https://example.com/clip.mp4", project_id="proj_test_vid")
        assert os.path.exists(dl_path)
        assert dl_path.endswith(".mp4")
        with open(dl_path, "rb") as f:
            content = f.read()
        assert content == fake_mp4
        if os.path.exists(dl_path):
            os.remove(dl_path)


def test_failed_download_handling():
    """7. Test error handling when HTTP download returns 404 or 500 error."""
    def mock_stream(method, url):
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_resp
        return mock_context

    with patch("httpx.Client.stream", side_effect=mock_stream):
        with pytest.raises(DownloaderError) as exc_info:
            MediaDownloader.download_asset("https://example.com/missing.png", project_id="proj_test_fail")
        assert "status code 404" in str(exc_info.value)


def test_unsupported_url_scheme():
    """8. Test rejection of unsupported non-HTTP URL schemes (e.g. ftp://)."""
    with pytest.raises(InvalidURLError) as exc_info:
        MediaDownloader.download_asset("ftp://example.com/file.png", project_id="proj_test_ftp")
    assert "Invalid HTTP/HTTPS URL" in str(exc_info.value)


def test_missing_ffmpeg_handling():
    """9. Test error propagation when FFmpeg binary is missing during environment validation."""
    FFmpegEngine._cached_exe = None
    with patch("app.services.rendering.ffmpeg.FFmpegEngine.get_ffmpeg_path", side_effect=FFmpegNotFoundError("FFmpeg executable not found")):
        res = FFmpegRenderer.render(RenderJobInput(
            project_id="proj_no_ffmpeg",
            timeline_id="tl_no_ffmpeg",
            scenes=[],
            output_dir="/tmp/no_ffmpeg_test"
        ))
        assert res.status == "FAILED"
        assert any("FFmpeg environment invalid" in log for log in res.logs)


def test_path_traversal_protection():
    """10. Test security path traversal protection in MediaDownloader."""
    # Ensure is_http_url returns True so resolve/download proceeds
    assert MediaDownloader.is_http_url("https://example.com/../../etc/passwd")

    with patch("app.services.rendering.downloader.MediaDownloader.get_assets_dir", return_value="/tmp/kidsai_renders/proj_safe/assets"):
        # The downloader uses url_hash for target path calculation, preventing path traversal
        fake_data = b"SECURE_DATA"
        def mock_stream(method, url):
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.headers = {"content-type": "image/png"}
            mock_resp.iter_bytes = MagicMock(return_value=[fake_data])
            mock_context = MagicMock()
            mock_context.__enter__.return_value = mock_resp
            return mock_context

        with patch("httpx.Client.stream", side_effect=mock_stream):
            target = MediaDownloader.download_asset("https://example.com/../../etc/passwd", project_id="proj_safe")
            assert "/tmp/kidsai_renders/proj_safe/assets" in target
            assert "passwd" not in os.path.basename(target)
            if os.path.exists(target):
                os.remove(target)


def test_render_failure_propagation():
    """11. Test render job failure propagation when an asset download fails."""
    def mock_stream(method, url):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_resp
        return mock_context

    with patch("httpx.Client.stream", side_effect=mock_stream):
        job = RenderJobInput(
            project_id="proj_fail_prop",
            timeline_id="tl_fail_prop",
            scenes=[
                SceneInput(
                    scene_number=1,
                    image_path="https://example.com/broken_image.png",
                    duration_seconds=3.0
                )
            ],
            output_dir="/tmp/kidsai_test_fail_prop"
        )
        res = FFmpegRenderer.render(job)
        assert res.status == "FAILED"
        assert any("Failed to download or prepare image asset" in log for log in res.logs)
