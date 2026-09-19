"""
Transition Engine for scene-to-scene transitions using FFmpeg xfade filter.
Supports Fade, Crossfade, Slide Left, Slide Right, Zoom, Dissolve, and Cut.
Ensures overall scene timing remains precise.
"""

from typing import Dict
from app.services.rendering.models import TransitionType
from app.services.rendering.config import rendering_settings


class TransitionEngine:
    # Map internal TransitionType enum to FFmpeg xfade filter names
    XFADE_MAPPING: Dict[TransitionType, str] = {
        TransitionType.FADE: "fade",
        TransitionType.CROSSFADE: "fade",
        TransitionType.SLIDE_LEFT: "slideleft",
        TransitionType.SLIDE_RIGHT: "slideright",
        TransitionType.ZOOM: "circlecrop",
        TransitionType.DISSOLVE: "dissolve",
        TransitionType.CUT: "fade"  # fallback handling
    }

    @classmethod
    def get_ffmpeg_transition_name(cls, transition: TransitionType) -> str:
        """Returns the corresponding FFmpeg xfade transition filter identifier."""
        return cls.XFADE_MAPPING.get(transition, "fade")

    @classmethod
    def build_xfade_filter(
        cls,
        stream_a: str,
        stream_b: str,
        output_stream: str,
        transition: TransitionType,
        duration_sec: float,
        offset_sec: float
    ) -> str:
        """
        Generates FFmpeg xfade complex filter syntax:
        e.g., [v0][v1]xfade=transition=slideleft:duration=0.5:offset=4.5[v_out]
        """
        dur = max(
            rendering_settings.transitions.min_duration_sec,
            min(duration_sec, rendering_settings.transitions.max_duration_sec)
        )
        offset = max(0.0, offset_sec)
        xfade_name = cls.get_ffmpeg_transition_name(transition)

        return f"{stream_a}{stream_b}xfade=transition={xfade_name}:duration={dur:.2f}:offset={offset:.2f}{output_stream}"
