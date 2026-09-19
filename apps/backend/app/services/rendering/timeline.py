"""
Timeline Builder Engine.
Builds scene timings, camera motion specs, transitions, and audio sync maps from project assets.
"""

import os
import json
from typing import Dict, Any, List, Optional
from app.services.rendering.models import (
    SceneInput, CameraDirection, TransitionType, AudioInput, SubtitleItem, RenderJobInput
)
from app.services.rendering.subtitles import SubtitleEngine


class TimelineEngine:
    @staticmethod
    def parse_camera_direction(val: Optional[str]) -> CameraDirection:
        """Normalizes camera direction strings to CameraDirection enum."""
        if not val:
            return CameraDirection.STATIC
        s = str(val).lower()
        if "in" in s or "zoom_in" in s:
            return CameraDirection.ZOOM_IN
        if "out" in s or "zoom_out" in s:
            return CameraDirection.ZOOM_OUT
        if "left" in s:
            return CameraDirection.PAN_LEFT
        if "right" in s:
            return CameraDirection.PAN_RIGHT
        if "up" in s:
            return CameraDirection.PAN_UP
        if "down" in s:
            return CameraDirection.PAN_DOWN
        if "dolly" in s:
            return CameraDirection.SLOW_DOLLY
        return CameraDirection.STATIC

    @staticmethod
    def parse_transition_type(val: Optional[str]) -> TransitionType:
        """Normalizes transition type strings to TransitionType enum."""
        if not val:
            return TransitionType.CROSSFADE
        s = str(val).lower()
        if "fade" in s and "black" in s:
            return TransitionType.FADE
        if "fade" in s:
            return TransitionType.CROSSFADE
        if "left" in s:
            return TransitionType.SLIDE_LEFT
        if "right" in s:
            return TransitionType.SLIDE_RIGHT
        if "zoom" in s:
            return TransitionType.ZOOM
        if "dissolve" in s:
            return TransitionType.DISSOLVE
        if "cut" in s:
            return TransitionType.CUT
        return TransitionType.CROSSFADE

    @classmethod
    def build_job_from_directory(cls, project_dir: str, output_dir: Optional[str] = None) -> RenderJobInput:
        """
        Scans a project directory containing:
        - storyboard.json or story.json
        - images/ (scene001.png, scene002.png, ...)
        - narration.wav / narration.mp3 or scene_X_narration.wav
        - music.mp3
        - subtitles.srt
        and constructs a complete RenderJobInput timeline.
        """
        storyboard_path = os.path.join(project_dir, "storyboard.json")
        story_path = os.path.join(project_dir, "story.json")
        images_dir = os.path.join(project_dir, "images")
        out_dir = output_dir or project_dir

        raw_scenes: List[Dict[str, Any]] = []

        if os.path.exists(storyboard_path):
            with open(storyboard_path, "r", encoding="utf-8") as f:
                sb_data = json.load(f)
                raw_scenes = sb_data.get("scenes", sb_data if isinstance(sb_data, list) else [])
        elif os.path.exists(story_path):
            with open(story_path, "r", encoding="utf-8") as f:
                st_data = json.load(f)
                raw_scenes = st_data.get("scenes", st_data if isinstance(st_data, list) else [])

        # Check subtitles file
        srt_path = os.path.join(project_dir, "subtitles.srt")
        parsed_subtitles: List[SubtitleItem] = []
        if os.path.exists(srt_path):
            parsed_subtitles = SubtitleEngine.parse_srt_file(srt_path)

        # Check global audio files
        music_path = None
        for m_ext in ["music.mp3", "music.wav", "bg_music.mp3"]:
            p = os.path.join(project_dir, m_ext)
            if os.path.exists(p):
                music_path = p
                break

        narration_path = None
        for n_ext in ["narration.wav", "narration.mp3", "voice.mp3", "voice.wav"]:
            p = os.path.join(project_dir, n_ext)
            if os.path.exists(p):
                narration_path = p
                break

        scenes: List[SceneInput] = []

        if not raw_scenes:
            # Fallback: scan images directory
            if os.path.exists(images_dir):
                img_files = sorted([f for f in os.listdir(images_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))])
                for idx, img_file in enumerate(img_files, start=1):
                    scenes.append(
                        SceneInput(
                            scene_number=idx,
                            image_path=os.path.join(images_dir, img_file),
                            duration_seconds=5.0,
                            camera_direction=CameraDirection.ZOOM_IN if idx % 2 == 1 else CameraDirection.PAN_RIGHT,
                            transition=TransitionType.CROSSFADE
                        )
                    )
        else:
            current_time = 0.0
            for idx, sc in enumerate(raw_scenes, start=1):
                scene_num = sc.get("scene_number", idx)
                dur = float(sc.get("duration", sc.get("estimated_duration", sc.get("duration_seconds", 5.0))))
                cam_dir = cls.parse_camera_direction(sc.get("camera_direction", sc.get("camera_motion", None)))
                zoom = float(sc.get("camera_zoom", 1.2))
                trans = cls.parse_transition_type(sc.get("transition", sc.get("transition_type", None)))
                trans_dur = float(sc.get("transition_duration", sc.get("transition_duration_seconds", 0.5)))

                # Locate scene image
                img_path = None
                img_candidates = [
                    os.path.join(images_dir, f"scene{scene_num:03d}.png"),
                    os.path.join(images_dir, f"scene{scene_num:03d}.jpg"),
                    os.path.join(images_dir, f"scene_{scene_num}.png"),
                    sc.get("image_path"),
                    sc.get("image_url")
                ]
                for cand in img_candidates:
                    if cand and os.path.exists(cand):
                        img_path = cand
                        break

                # Locate scene narration
                sc_narration = None
                sc_nar_candidates = [
                    os.path.join(project_dir, f"scene_{scene_num}_narration.wav"),
                    os.path.join(project_dir, f"scene_{scene_num}_narration.mp3"),
                    sc.get("narration_path"),
                    sc.get("voice_url")
                ]
                for cand in sc_nar_candidates:
                    if cand and os.path.exists(cand):
                        sc_narration = cand
                        break

                # Extract matching subtitles for this scene timestamp range
                scene_start = current_time
                scene_end = current_time + dur
                sc_subs = [
                    sub for sub in parsed_subtitles
                    if sub.start_time_sec < scene_end and sub.end_time_sec > scene_start
                ]

                scenes.append(
                    SceneInput(
                        scene_number=scene_num,
                        image_path=img_path,
                        duration_seconds=dur,
                        camera_direction=cam_dir,
                        camera_zoom=zoom,
                        transition=trans,
                        transition_duration_seconds=trans_dur,
                        narration_path=sc_narration,
                        subtitles=sc_subs
                    )
                )

                current_time += dur

        return RenderJobInput(
            project_id=os.path.basename(project_dir) or "proj_default",
            timeline_id=f"tl_{os.path.basename(project_dir)}",
            scenes=scenes,
            music_path=music_path,
            subtitles_path=srt_path if os.path.exists(srt_path) else None,
            output_dir=out_dir
        )
