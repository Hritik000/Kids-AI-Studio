"""
Camera Engine for FFmpeg zoompan filter expressions.
Generates dynamic camera motion filters: Zoom In, Zoom Out, Pan Left, Pan Right,
Pan Up, Pan Down, Slow Dolly, and Static.
"""

import math
from app.services.rendering.models import CameraDirection
from app.services.rendering.config import rendering_settings


class CameraEngine:
    @staticmethod
    def build_camera_filter(
        direction: CameraDirection,
        duration_seconds: float,
        width: int = 1920,
        height: int = 1080,
        fps: int = 30,
        zoom_ratio: float = 1.25
    ) -> str:
        """
        Generates an FFmpeg complex filter snippet combining scale/crop and zoompan.
        Output filter pads/scales input image to specified width and height.
        """
        total_frames = max(1, int(round(duration_seconds * fps)))
        z_ratio = max(1.05, zoom_ratio or rendering_settings.camera.default_zoom_ratio)

        # Base preprocessing: ensure input is scaled to 1920x1080
        prep = f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}"

        if direction == CameraDirection.ZOOM_IN:
            # Zoom from 1.0 to z_ratio centered
            step = (z_ratio - 1.0) / total_frames
            z_expr = f"min(1.0+on*{step:.6f},{z_ratio:.3f})"
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = "ih/2-(ih/zoom/2)"

        elif direction == CameraDirection.ZOOM_OUT:
            # Zoom from z_ratio down to 1.0 centered
            step = (z_ratio - 1.0) / total_frames
            z_expr = f"max({z_ratio:.3f}-on*{step:.6f},1.0)"
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = "ih/2-(ih/zoom/2)"

        elif direction == CameraDirection.PAN_LEFT:
            # Fixed zoom, pan from right to left
            z_expr = f"{z_ratio:.3f}"
            x_expr = f"(1-on/{total_frames})*(iw-iw/zoom)"
            y_expr = "ih/2-(ih/zoom/2)"

        elif direction == CameraDirection.PAN_RIGHT:
            # Fixed zoom, pan from left to right
            z_expr = f"{z_ratio:.3f}"
            x_expr = f"(on/{total_frames})*(iw-iw/zoom)"
            y_expr = "ih/2-(ih/zoom/2)"

        elif direction == CameraDirection.PAN_UP:
            # Fixed zoom, pan from bottom to top
            z_expr = f"{z_ratio:.3f}"
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = f"(1-on/{total_frames})*(ih-ih/zoom)"

        elif direction == CameraDirection.PAN_DOWN:
            # Fixed zoom, pan from top to bottom
            z_expr = f"{z_ratio:.3f}"
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = f"(on/{total_frames})*(ih-ih/zoom)"

        elif direction == CameraDirection.SLOW_DOLLY:
            # Subtle zoom in with central alignment
            dolly_scale = rendering_settings.camera.slow_dolly_scale
            step = (dolly_scale - 1.0) / total_frames
            z_expr = f"min(1.0+on*{step:.6f},{dolly_scale:.3f})"
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = "ih/2-(ih/zoom/2)"

        else:  # STATIC
            z_expr = "1.0"
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = "ih/2-(ih/zoom/2)"

        zoompan_filter = (
            f"zoompan=z='{z_expr}':x='{x_expr}':y='{y_expr}':"
            f"d={total_frames}:s={width}x{height}:fps={fps}"
        )

        return f"{prep},{zoompan_filter}"
