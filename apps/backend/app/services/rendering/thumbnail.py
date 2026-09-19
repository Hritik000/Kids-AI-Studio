"""
Thumbnail Extraction Engine.
Generates thumbnail.jpg from rendered video at specified frame timestamp or middle frame.
"""

import os
from typing import Optional
from app.services.rendering.ffmpeg import FFmpegEngine


class ThumbnailEngine:
    @staticmethod
    def extract_thumbnail(
        video_path: str,
        output_thumbnail_path: str,
        timestamp_sec: float = 2.0,
        quality: int = 2
    ) -> str:
        """
        Extracts a single JPEG image frame from a video at timestamp_sec using FFmpeg.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Cannot extract thumbnail: video file not found at '{video_path}'")

        timestamp_str = f"{timestamp_sec:.2f}"
        args = [
            "-ss", timestamp_str,
            "-i", video_path,
            "-frames:v", "1",
            "-q:v", str(quality),
            output_thumbnail_path
        ]

        FFmpegEngine.run_command(args, timeout=30)
        return output_thumbnail_path
