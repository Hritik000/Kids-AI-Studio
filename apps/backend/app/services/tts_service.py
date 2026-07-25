from typing import List
from app.models.project import Scene
from app.core.adapters.tts_adapter import tts_adapter

class TTSService:
    async def generate_narration_audio(self, project_id: str, scenes: List[Scene]) -> List[Scene]:
        updated_scenes = []
        for scene in scenes:
            audio_path = await tts_adapter.generate_speech(
                scene.narration_text,
                project_id,
                scene.scene_number
            )
            scene.audio_url = audio_path
            # Set duration based on audio file length or word estimate
            word_count = len(scene.narration_text.split())
            scene.duration_seconds = max(3.0, round(word_count / 3.0, 1))
            updated_scenes.append(scene)
        return updated_scenes

tts_service = TTSService()
