"""
Audio Engine for multi-track audio mixing, speech ducking, loudness normalization, and audio fading.
Mixes narration speech and background music.
"""

from typing import List, Optional
from app.services.rendering.config import rendering_settings, AudioOutputConfig


class AudioEngine:
    @staticmethod
    def build_audio_mix_filter(
        has_narration: bool,
        has_music: bool,
        total_duration_sec: float,
        config: Optional[AudioOutputConfig] = None
    ) -> str:
        """
        Generates FFmpeg complex filter syntax for audio mixing.
        Assumes narration is stream [nar_a] (if present) and music is stream [music_a] (if present).
        """
        cfg = config or rendering_settings.audio

        if not has_narration and not has_music:
            # Generate silent audio stream matching duration
            return f"anullsrc=channel_layout=stereo:sample_rate={cfg.sample_rate}[a_out]"

        if has_narration and not has_music:
            # Normalize narration audio loudness
            return f"[nar_a]loudnorm=I={cfg.target_lufs}:TP={cfg.max_peak_db}[a_out]"

        if has_music and not has_narration:
            # Apply fade in/out and loudness normalization to background music
            fade_out_start = max(0.0, total_duration_sec - cfg.music_fade_out_sec)
            music_fades = (
                f"[music_a]afade=t=in:ss=0:d={cfg.music_fade_in_sec},"
                f"afade=t=out:st={fade_out_start:.2f}:d={cfg.music_fade_out_sec}[m_faded];"
                f"[m_faded]loudnorm=I={cfg.target_lufs}:TP={cfg.max_peak_db}[a_out]"
            )
            return music_fades

        # Both Narration and Music are present -> Apply Sidechain Compress Ducking (-12dB) & Loudnorm
        fade_out_start = max(0.0, total_duration_sec - cfg.music_fade_out_sec)
        ducking_filter = (
            # 1. Split narration stream for audio output and sidechain trigger
            "[nar_a]asplit=2[nar_mix][nar_sc];"
            # 2. Fade music in/out
            f"[music_a]afade=t=in:ss=0:d={cfg.music_fade_in_sec},"
            f"afade=t=out:st={fade_out_start:.2f}:d={cfg.music_fade_out_sec}[music_faded];"
            # 3. Sidechain compress music using narration trigger
            f"[music_faded][nar_sc]sidechaincompress="
            f"threshold=0.03:ratio=4:attack={cfg.ducking_attack_ms}:release={cfg.ducking_release_ms}[music_ducked];"
            # 4. Mix speech + ducked background music
            "[nar_mix][music_ducked]amix=inputs=2:duration=first:dropout_transition=2[audio_unnormalized];"
            # 5. Normalize overall mix to target LUFS (-14.0 LUFS)
            f"[audio_unnormalized]loudnorm=I={cfg.target_lufs}:TP={cfg.max_peak_db}[a_out]"
        )

        return ducking_filter
