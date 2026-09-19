"""
Subtitle Overlay Engine.
Parses SRT/VTT files or subtitle items, generates styled ASS subtitle files,
and builds FFmpeg subtitle filter expressions with font, outline, shadow,
alignment, and safe margin specifications.
"""

import os
import re
from typing import List, Optional
from app.services.rendering.models import SubtitleItem
from app.services.rendering.config import rendering_settings, SubtitleStyleConfig


class SubtitleEngine:
    @staticmethod
    def parse_srt_file(srt_path: str) -> List[SubtitleItem]:
        """Parses an SRT subtitle file into a list of SubtitleItem objects."""
        if not os.path.exists(srt_path):
            return []

        items: List[SubtitleItem] = []
        with open(srt_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        blocks = re.split(r"\n\s*\n", content.strip())
        for idx, block in enumerate(blocks, start=1):
            lines = block.strip().splitlines()
            if len(lines) >= 3:
                time_match = re.match(
                    r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[,.](\d{3})",
                    lines[1].strip()
                )
                if time_match:
                    h1, m1, s1, ms1, h2, m2, s2, ms2 = map(int, time_match.groups())
                    start_sec = h1 * 3600 + m1 * 60 + s1 + ms1 / 1000.0
                    end_sec = h2 * 3600 + m2 * 60 + s2 + ms2 / 1000.0
                    text = " ".join(lines[2:]).strip()
                    items.append(
                        SubtitleItem(
                            index=idx,
                            start_time_sec=start_sec,
                            end_time_sec=end_sec,
                            text=text
                        )
                    )

        return items

    @staticmethod
    def format_ass_timestamp(seconds: float) -> str:
        """Converts floating point seconds to ASS timestamp format H:MM:SS.cs"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        cs = int(round((seconds - int(seconds)) * 100))
        if cs >= 100:
            cs = 99
        return f"{hours}:{minutes:02d}:{secs:02d}.{cs:02d}"

    @classmethod
    def generate_ass_subtitle_file(
        cls,
        subtitles: List[SubtitleItem],
        output_ass_path: str,
        style: Optional[SubtitleStyleConfig] = None
    ) -> str:
        """Generates an Advanced SubStation Alpha (.ass) subtitle file with custom formatting."""
        s = style or rendering_settings.subtitles

        ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{s.font_name},{s.font_size},{s.primary_color},&H000000FF,{s.outline_color},{s.back_color},{1 if s.bold else 0},{1 if s.italic else 0},0,0,100,100,0,0,1,{s.outline_width:.1f},{s.shadow_depth:.1f},{s.alignment},{s.margin_l},{s.margin_r},{s.margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        events = []
        for sub in subtitles:
            start_ts = cls.format_ass_timestamp(sub.start_time_sec)
            end_ts = cls.format_ass_timestamp(sub.end_time_sec)
            clean_text = sub.text.replace("\n", "\\N")
            events.append(f"Dialogue: 0,{start_ts},{end_ts},Default,,0,0,0,,{clean_text}")

        full_ass_content = ass_header + "\n".join(events) + "\n"

        with open(output_ass_path, "w", encoding="utf-8") as f:
            f.write(full_ass_content)

        return output_ass_path

    @classmethod
    def build_subtitle_filter(
        cls,
        subtitle_file_path: str,
        style: Optional[SubtitleStyleConfig] = None
    ) -> str:
        """
        Builds the FFmpeg filter string for rendering subtitles.
        Handles proper path escaping for colons and backslashes in FFmpeg filter syntax.
        """
        escaped_path = subtitle_file_path.replace("\\", "/").replace(":", "\\:")

        if subtitle_file_path.endswith(".ass"):
            return f"ass='{escaped_path}'"

        s = style or rendering_settings.subtitles
        force_style = (
            f"FontName={s.font_name},"
            f"FontSize={s.font_size},"
            f"PrimaryColour={s.primary_color},"
            f"OutlineColour={s.outline_color},"
            f"BackColour={s.back_color},"
            f"Bold={1 if s.bold else 0},"
            f"Outline={s.outline_width},"
            f"Shadow={s.shadow_depth},"
            f"Alignment={s.alignment},"
            f"MarginV={s.margin_v}"
        )

        return f"subtitles='{escaped_path}':force_style='{force_style}'"
