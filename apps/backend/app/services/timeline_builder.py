import uuid
from typing import Dict, Any, List, Optional
from app.models.rendering import VideoTimeline, TimelineSceneItem, SubtitlePlaceholder
from app.core.mock_media import create_mock_png

class TimelineBuilderService:
    @staticmethod
    def build_timeline(
        project_id: str,
        storyboard: Dict[str, Any],
        animations: List[Dict[str, Any]],
        voices: List[Dict[str, Any]],
        music_mixes: List[Dict[str, Any]],
        aspect_ratio: str = "16:9"
    ) -> VideoTimeline:
        scenes = storyboard.get("scenes", [])
        timeline_scenes: List[TimelineSceneItem] = []
        total_duration = 0.0

        for idx, scene in enumerate(scenes, 1):
            scene_num = scene.get("scene_number", idx)
            est_dur = float(scene.get("estimated_duration", 5.0))

            # Match animation clip
            anim_match = next((a for a in animations if a.get("scene_number") == scene_num), None)
            if anim_match:
                anim_url = anim_match.get("storage_url")
            else:
                width, height = (640, 360) if aspect_ratio == "16:9" else (360, 640)
                anim_url = create_mock_png(
                    project_id=project_id,
                    asset_name=f"asset_timeline_placeholder_scene_{scene_num}.png",
                    width=width,
                    height=height,
                    color=(26, 29, 39),
                )

            # Match voice narration clip
            voice_match = next((v for v in voices if v.get("scene_number") == scene_num), None)
            voice_url = voice_match.get("storage_url") if voice_match else None

            # Match music audio mix clip
            music_match = next((m for m in music_mixes if m.get("scene_number") == scene_num), None)
            music_url = music_match.get("storage_url") if music_match else None

            # Determine transition
            trans_type = "CrossFade" if idx < len(scenes) else "Cut"

            item = TimelineSceneItem(
                scene_number=scene_num,
                duration_seconds=est_dur,
                animation_url=anim_url,
                voice_url=voice_url,
                music_mix_url=music_url,
                transition_type=trans_type,
                transition_duration_seconds=0.5,
                subtitle_placeholder=SubtitlePlaceholder()
            )
            timeline_scenes.append(item)
            total_duration += est_dur

        return VideoTimeline(
            timeline_id=f"tl_{project_id}_{uuid.uuid4().hex[:6]}",
            project_id=project_id,
            aspect_ratio=aspect_ratio,
            resolution="1080p",
            frame_rate=24,
            total_duration_seconds=total_duration,
            scenes=timeline_scenes
        )
