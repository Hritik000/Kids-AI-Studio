import uuid
import time
from typing import List, Dict, Any, Optional
from app.models.music import MixedAudioTrack, MusicPlan, SoundEffectItem, AmbientAudioPlan
from app.core.music_provider import get_music_provider, MusicProvider
from app.services.music_planner import MusicPlannerService
from app.services.sound_effects import SoundEffectService
from app.services.ambient_audio import AmbientAudioService
from app.services.music_validator import MusicValidationService, MusicValidationError
from app.core.llm import PromptLoader

# In-memory repository for Mixed Audio Tracks
music_mixes_db: Dict[str, List[MixedAudioTrack]] = {}

class MusicPipelineService:
    def __init__(self, music_provider: Optional[MusicProvider] = None):
        self.provider = music_provider or get_music_provider()

    async def generate_all_scene_music_mixes(
        self,
        project_id: str,
        storyboard: Dict[str, Any],
        production_plan: Optional[Dict[str, Any]] = None
    ) -> List[MixedAudioTrack]:
        scenes = storyboard.get("scenes", [])
        master_music_plan = MusicPlannerService.plan_music_for_project(storyboard, production_plan)
        generated_mixes: List[MixedAudioTrack] = []

        for idx, scene in enumerate(scenes, 1):
            scene_num = scene.get("scene_number", idx)
            est_duration = float(scene.get("estimated_duration", 5.0))
            
            # 1. Generate SFX and Ambient plans
            sfx_items = SoundEffectService.generate_sound_effects_for_scene(scene, scene_num)
            ambient_plan = AmbientAudioService.generate_ambient_plan_for_scene(scene)

            # 2. Compose Music Prompt
            music_prompt = PromptLoader.load_prompt("music.md", {
                "genre": master_music_plan.genre,
                "mood": master_music_plan.mood,
                "bpm": master_music_plan.bpm,
                "instruments": ", ".join(master_music_plan.instruments),
                "target_age_group": "3-5"
            })

            start_time = time.time()
            raw_output = await self.provider.synthesize_music_and_mix(
                prompt=music_prompt,
                duration_seconds=est_duration,
                bpm=master_music_plan.bpm
            )
            duration = round(time.time() - start_time, 2)

            mix_record = MixedAudioTrack(
                mix_id=f"mix_{project_id}_{scene_num}_{uuid.uuid4().hex[:6]}",
                project_id=project_id,
                scene_number=scene_num,
                music_plan=master_music_plan,
                sound_effects=sfx_items,
                ambient_plan=ambient_plan,
                narration_volume=1.0,
                music_ducked_volume=0.25,
                ambient_volume=0.15,
                sfx_volume=0.5,
                master_loudness_lufs=-14.0,
                duration_seconds=est_duration,
                sample_rate=44100,
                audio_format="MP3",
                provider=raw_output.get("provider", "StableAudio-Open-v1"),
                storage_url=raw_output["storage_url"],
                generation_time_seconds=duration,
                status="GENERATED"
            )

            # Validate Mixed Track Record
            MusicValidationService.validate_mixed_track(mix_record.model_dump())
            generated_mixes.append(mix_record)

        music_mixes_db[project_id] = generated_mixes
        return generated_mixes

    async def regenerate_single_scene_music(
        self,
        project_id: str,
        scene_number: int,
        storyboard: Dict[str, Any]
    ) -> MixedAudioTrack:
        existing_mixes = music_mixes_db.get(project_id, [])
        scenes = storyboard.get("scenes", [])
        scene = next((s for s in scenes if s.get("scene_number") == scene_number), {})
        est_duration = float(scene.get("estimated_duration", 5.0))

        master_music_plan = MusicPlannerService.plan_music_for_project(storyboard)
        sfx_items = SoundEffectService.generate_sound_effects_for_scene(scene, scene_number)
        ambient_plan = AmbientAudioService.generate_ambient_plan_for_scene(scene)

        music_prompt = PromptLoader.load_prompt("music.md", {
            "genre": master_music_plan.genre,
            "mood": master_music_plan.mood,
            "bpm": master_music_plan.bpm,
            "instruments": ", ".join(master_music_plan.instruments),
            "target_age_group": "3-5"
        })

        start_time = time.time()
        raw_output = await self.provider.synthesize_music_and_mix(
            prompt=music_prompt,
            duration_seconds=est_duration,
            bpm=master_music_plan.bpm
        )
        duration = round(time.time() - start_time, 2)

        new_mix = MixedAudioTrack(
            mix_id=f"mix_{project_id}_{scene_number}_{uuid.uuid4().hex[:6]}",
            project_id=project_id,
            scene_number=scene_number,
            music_plan=master_music_plan,
            sound_effects=sfx_items,
            ambient_plan=ambient_plan,
            narration_volume=1.0,
            music_ducked_volume=0.25,
            ambient_volume=0.15,
            sfx_volume=0.5,
            master_loudness_lufs=-14.0,
            duration_seconds=est_duration,
            sample_rate=44100,
            audio_format="MP3",
            provider=raw_output.get("provider", "StableAudio-Open-v1"),
            storage_url=raw_output["storage_url"],
            generation_time_seconds=duration,
            status="GENERATED"
        )

        updated_list = [m for m in existing_mixes if m.scene_number != scene_number]
        updated_list.append(new_mix)
        updated_list.sort(key=lambda x: x.scene_number)
        music_mixes_db[project_id] = updated_list

        return new_mix
