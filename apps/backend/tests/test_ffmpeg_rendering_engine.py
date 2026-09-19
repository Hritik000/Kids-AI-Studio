"""
Comprehensive Unit & Integration Tests for Industry-Grade FFmpeg Rendering Engine.
Tests:
- Environment & Asset Validation
- Camera Motion Filter Syntax
- Transition xfade Filter Syntax
- Subtitle Parsing & ASS Generation
- Audio Mixing & Ducking Filters
- Real End-to-End FFmpeg MP4 Render & Thumbnail Extraction
"""

import os
import tempfile
import pytest
from app.services.rendering import (
    FFmpegEngine, RenderValidatorService, CameraEngine, CameraDirection,
    TransitionEngine, TransitionType, SubtitleEngine, SubtitleItem,
    AudioEngine, ThumbnailEngine, TimelineEngine, FFmpegRenderer, RenderJobInput, SceneInput
)
from app.services.rendering.config import rendering_settings


def test_ffmpeg_engine_version_and_environment():
    """Verify FFmpeg binary detection and version reporting."""
    result = RenderValidatorService.validate_render_environment()
    assert result.is_valid is True
    assert result.ffmpeg_version is not None
    assert "ffmpeg version" in result.ffmpeg_version.lower()


def test_camera_engine_directions():
    """Test filter generation for all 8 camera motion directions."""
    directions = [
        CameraDirection.ZOOM_IN,
        CameraDirection.ZOOM_OUT,
        CameraDirection.PAN_LEFT,
        CameraDirection.PAN_RIGHT,
        CameraDirection.PAN_UP,
        CameraDirection.PAN_DOWN,
        CameraDirection.SLOW_DOLLY,
        CameraDirection.STATIC
    ]

    for direction in directions:
        filter_str = CameraEngine.build_camera_filter(
            direction=direction,
            duration_seconds=3.0,
            width=1920,
            height=1080,
            fps=30
        )
        assert "scale=1920:1080" in filter_str
        assert "zoompan=" in filter_str
        assert "s=1920x1080" in filter_str


def test_transition_engine_filters():
    """Test xfade filter string creation for supported transitions."""
    transitions = [
        TransitionType.FADE,
        TransitionType.CROSSFADE,
        TransitionType.SLIDE_LEFT,
        TransitionType.SLIDE_RIGHT,
        TransitionType.ZOOM,
        TransitionType.DISSOLVE,
        TransitionType.CUT
    ]

    for trans in transitions:
        filter_str = TransitionEngine.build_xfade_filter(
            stream_a="[v0]",
            stream_b="[v1]",
            output_stream="[v_out]",
            transition=trans,
            duration_sec=0.5,
            offset_sec=4.5
        )
        assert "[v0][v1]xfade=transition=" in filter_str
        assert "duration=0.50" in filter_str
        assert "offset=4.50" in filter_str
        assert "[v_out]" in filter_str


def test_subtitle_parsing_and_ass_generation():
    """Test SRT parsing and ASS file generation."""
    srt_content = """1
00:00:01,000 --> 00:00:03,500
Hello kids, welcome to KidsAI Studio!

2
00:00:04,000 --> 00:00:06,200
Let's learn about dinosaurs today.
"""
    with tempfile.NamedTemporaryFile(suffix=".srt", mode="w", delete=False, encoding="utf-8") as f:
        f.write(srt_content)
        srt_path = f.name

    try:
        items = SubtitleEngine.parse_srt_file(srt_path)
        assert len(items) == 2
        assert items[0].start_time_sec == 1.0
        assert items[0].end_time_sec == 3.5
        assert "KidsAI Studio" in items[0].text

        ass_path = srt_path.replace(".srt", ".ass")
        SubtitleEngine.generate_ass_subtitle_file(items, ass_path)
        assert os.path.exists(ass_path)

        with open(ass_path, "r", encoding="utf-8") as af:
            ass_content = af.read()
            assert "[Script Info]" in ass_content
            assert "PlayResX: 1920" in ass_content
            assert "Dialogue: 0,0:00:01.00" in ass_content
    finally:
        if os.path.exists(srt_path):
            os.remove(srt_path)
        if os.path.exists(ass_path):
            os.remove(ass_path)


def test_audio_engine_ducking_filter():
    """Test sidechain ducking and loudness normalization filter graph generation."""
    filter_ducking = AudioEngine.build_audio_mix_filter(
        has_narration=True,
        has_music=True,
        total_duration_sec=10.0
    )
    assert "sidechaincompress=" in filter_ducking
    assert "loudnorm=I=-14" in filter_ducking
    assert "afade=t=in" in filter_ducking
    assert "afade=t=out" in filter_ducking


def test_end_to_end_real_ffmpeg_rendering():
    """Real end-to-end integration test creating a 1080p MP4 video and thumbnail."""
    with tempfile.TemporaryDirectory(prefix="test_render_e2e_") as project_dir:
        images_dir = os.path.join(project_dir, "images")
        os.makedirs(images_dir, exist_ok=True)

        # 1. Create 2 synthetic test PNG images using FFmpeg
        img1 = os.path.join(images_dir, "scene001.png")
        img2 = os.path.join(images_dir, "scene002.png")

        FFmpegEngine.run_command([
            "-f", "lavfi", "-i", "color=c=blue:s=1920x1080",
            "-frames:v", "1", img1
        ])
        FFmpegEngine.run_command([
            "-f", "lavfi", "-i", "color=c=red:s=1920x1080",
            "-frames:v", "1", img2
        ])

        assert os.path.exists(img1)
        assert os.path.exists(img2)

        # 2. Create synthetic WAV narration audio file
        audio1 = os.path.join(project_dir, "narration.wav")
        FFmpegEngine.run_command([
            "-f", "lavfi", "-i", "sine=frequency=440:duration=4",
            "-c:a", "pcm_s16le", audio1
        ])

        # 3. Create synthetic SRT subtitle file
        srt_path = os.path.join(project_dir, "subtitles.srt")
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write("1\n00:00:00,500 --> 00:00:03,500\nTesting real FFmpeg rendering pipeline!\n")

        # 4. Construct RenderJobInput
        job = RenderJobInput(
            project_id="proj_test_e2e",
            timeline_id="tl_test_e2e",
            scenes=[
                SceneInput(
                    scene_number=1,
                    image_path=img1,
                    duration_seconds=3.0,
                    camera_direction=CameraDirection.ZOOM_IN,
                    transition=TransitionType.CROSSFADE,
                    transition_duration_seconds=0.5,
                    narration_path=audio1
                ),
                SceneInput(
                    scene_number=2,
                    image_path=img2,
                    duration_seconds=3.0,
                    camera_direction=CameraDirection.PAN_RIGHT,
                    transition=TransitionType.SLIDE_LEFT,
                    transition_duration_seconds=0.5
                )
            ],
            subtitles_path=srt_path,
            output_dir=project_dir
        )

        # 5. Execute full FFmpeg render pipeline
        result = FFmpegRenderer.render(job)

        # 6. Verify result
        assert result.status == "COMPLETED"
        assert os.path.exists(result.final_video_path)
        assert os.path.exists(result.thumbnail_path)
        assert result.file_size_bytes > 0
        assert result.final_video_path.endswith(".mp4")
        assert result.thumbnail_path.endswith(".jpg")
