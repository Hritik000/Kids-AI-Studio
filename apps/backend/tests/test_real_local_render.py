"""
Deterministic Real Local FFmpeg Render Integration Test.
Generates synthetic local image and audio assets, invokes real FFmpeg binary,
renders an actual 1080p MP4 file, and verifies output integrity.
"""

import os
import wave
import math
import struct
import tempfile
import pytest
from app.services.rendering import (
    FFmpegEngine, FFmpegRenderer, RenderJobInput, SceneInput, CameraDirection, TransitionType
)


def create_synthetic_image(file_path: str, width: int = 1280, height: int = 720, color_rgb: tuple = (30, 144, 255)):
    """Generates a synthetic PNG image using FFmpeg lavfi color generator."""
    r, g, b = color_rgb
    hex_color = f"0x{r:02x}{g:02x}{b:02x}"
    FFmpegEngine.run_command([
        "-f", "lavfi",
        "-i", f"color=c={hex_color}:s={width}x{height}",
        "-frames:v", "1",
        file_path
    ])


def create_synthetic_audio(file_path: str, duration_sec: float = 2.0, freq: int = 440, sample_rate: int = 44100):
    """Generates a synthetic PCM WAV audio file using standard library wave module."""
    num_samples = int(duration_sec * sample_rate)
    with wave.open(file_path, "w") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)

        raw_bytes = bytearray()
        for i in range(num_samples):
            val = int(32767.0 * math.sin(2.0 * math.pi * freq * i / sample_rate))
            raw_bytes.extend(struct.pack("<h", val))
        wav_file.writeframes(raw_bytes)


def test_real_local_render_execution():
    """Real deterministic end-to-end local FFmpeg render test."""
    with tempfile.TemporaryDirectory(prefix="real_local_render_test_") as work_dir:
        output_dir = os.path.join(work_dir, "output")
        os.makedirs(output_dir, exist_ok=True)

        # 1. Create synthetic local test image (blue 1280x720 PNG)
        img_path = os.path.join(work_dir, "test_hero_image.png")
        create_synthetic_image(img_path, width=1280, height=720, color_rgb=(30, 144, 255))
        assert os.path.exists(img_path)
        assert os.path.getsize(img_path) > 0

        # 2. Create synthetic local narration audio file (2-second 440Hz WAV)
        audio_path = os.path.join(work_dir, "test_narration.wav")
        create_synthetic_audio(audio_path, duration_sec=2.0, freq=440)
        assert os.path.exists(audio_path)
        assert os.path.getsize(audio_path) > 0

        # 3. Construct RenderJobInput with local files
        job = RenderJobInput(
            project_id="proj_real_local_test",
            timeline_id="tl_real_local_test",
            scenes=[
                SceneInput(
                    scene_number=1,
                    image_path=img_path,
                    duration_seconds=3.0,
                    camera_direction=CameraDirection.ZOOM_IN,
                    transition=TransitionType.CROSSFADE,
                    narration_path=audio_path
                )
            ],
            output_dir=output_dir,
            resolution="1080p",
            codec="H.264"
        )

        # 4. Invoke actual FFmpeg Renderer Engine
        result = FFmpegRenderer.render(job)

        # 5. Assertions
        assert result.status == "COMPLETED", f"Render failed with logs: {result.logs}"
        assert os.path.isfile(result.final_video_path), "Output MP4 file does not exist"
        assert result.file_size_bytes > 0, "Output MP4 file is 0 bytes"
        assert os.path.isfile(result.thumbnail_path), "Output thumbnail JPEG does not exist"
        assert os.path.getsize(result.thumbnail_path) > 0, "Thumbnail JPEG is 0 bytes"

        # 6. Verify that FFmpeg can inspect the resulting MP4 file
        try:
            ret_code, stdout, stderr = FFmpegEngine.run_command(["-i", result.final_video_path], timeout=15)
        except Exception as e:
            # FFmpeg returns exit code 1 when invoked with -i without output file, but outputs media info in stderr
            stderr = getattr(e, "stderr", str(e))

        probe_info = stderr or ""
        assert "Input #0, mov,mp4,m4a" in probe_info or "Video:" in probe_info, f"FFmpeg inspection failed: {probe_info}"
