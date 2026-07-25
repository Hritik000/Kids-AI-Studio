import uuid
import time
from typing import List, Dict, Any, Optional
from app.models.audio import VoiceNarrationAsset, DialogueSegment, LipSyncMetadata
from app.core.voice_provider import get_voice_provider, VoiceProvider
from app.services.dialogue_planner import DialoguePlannerService
from app.services.lip_sync import LipSyncEngineService
from app.services.audio_processor import AudioProcessorService
from app.services.audio_validator import AudioValidationService, AudioValidationError
from app.core.llm import PromptLoader

# In-memory repository for Voice Narration Assets
audios_db: Dict[str, List[VoiceNarrationAsset]] = {}

class VoicePipelineService:
    def __init__(self, voice_provider: Optional[VoiceProvider] = None):
        self.provider = voice_provider or get_voice_provider()

    async def generate_all_scene_voices(
        self,
        project_id: str,
        storyboard: Dict[str, Any],
        voice_name: str = "Storyteller Emma",
        language: str = "English (US)"
    ) -> List[VoiceNarrationAsset]:
        scenes = storyboard.get("scenes", [])
        generated_audios: List[VoiceNarrationAsset] = []

        for idx, scene in enumerate(scenes, 1):
            scene_num = scene.get("scene_number", idx)
            est_duration = float(scene.get("estimated_duration", 5.0))
            
            # 1. Dialogue Planning
            dialogue_segs = DialoguePlannerService.plan_dialogue_for_scene(scene, scene_num)
            full_text = " ".join([seg.text for seg in dialogue_segs])

            # 2. Lip Sync Generation
            lip_sync = LipSyncEngineService.generate_lip_sync_timeline(dialogue_segs, est_duration)

            start_time = time.time()
            raw_output = await self.provider.synthesize_speech(
                text=full_text,
                voice_name=voice_name,
                emotion=scene.get("visual_plan", {}).get("mood", "Cheerful"),
                language=language
            )
            proc_duration = round(time.time() - start_time, 2)

            audio_record = VoiceNarrationAsset(
                audio_id=f"aud_{project_id}_{scene_num}_{uuid.uuid4().hex[:6]}",
                project_id=project_id,
                scene_number=scene_num,
                dialogue_segments=dialogue_segs,
                lip_sync=lip_sync,
                voice_name=voice_name,
                emotion=scene.get("visual_plan", {}).get("mood", "Cheerful"),
                language=language,
                duration_seconds=est_duration,
                provider=raw_output.get("provider", "KokoroTTS-v1"),
                storage_url=raw_output["storage_url"],
                generation_time_seconds=proc_duration,
                status="GENERATED"
            )

            # Validate Audio Record
            AudioValidationService.validate_audio(audio_record.model_dump())
            generated_audios.append(audio_record)

        audios_db[project_id] = generated_audios
        return generated_audios

    async def regenerate_single_scene_voice(
        self,
        project_id: str,
        scene_number: int,
        storyboard: Dict[str, Any],
        voice_name: str = "Storyteller Emma",
        language: str = "English (US)"
    ) -> VoiceNarrationAsset:
        existing_audios = audios_db.get(project_id, [])
        scenes = storyboard.get("scenes", [])
        scene = next((s for s in scenes if s.get("scene_number") == scene_number), {})
        est_duration = float(scene.get("estimated_duration", 5.0))

        dialogue_segs = DialoguePlannerService.plan_dialogue_for_scene(scene, scene_number)
        full_text = " ".join([seg.text for seg in dialogue_segs])
        lip_sync = LipSyncEngineService.generate_lip_sync_timeline(dialogue_segs, est_duration)

        start_time = time.time()
        raw_output = await self.provider.synthesize_speech(
            text=full_text,
            voice_name=voice_name,
            emotion=scene.get("visual_plan", {}).get("mood", "Cheerful"),
            language=language
        )
        proc_duration = round(time.time() - start_time, 2)

        new_audio = VoiceNarrationAsset(
            audio_id=f"aud_{project_id}_{scene_number}_{uuid.uuid4().hex[:6]}",
            project_id=project_id,
            scene_number=scene_number,
            dialogue_segments=dialogue_segs,
            lip_sync=lip_sync,
            voice_name=voice_name,
            emotion=scene.get("visual_plan", {}).get("mood", "Cheerful"),
            language=language,
            duration_seconds=est_duration,
            provider=raw_output.get("provider", "KokoroTTS-v1"),
            storage_url=raw_output["storage_url"],
            generation_time_seconds=proc_duration,
            status="GENERATED"
        )

        updated_list = [aud for aud in existing_audios if aud.scene_number != scene_number]
        updated_list.append(new_audio)
        updated_list.sort(key=lambda x: x.scene_number)
        audios_db[project_id] = updated_list

        return new_audio
