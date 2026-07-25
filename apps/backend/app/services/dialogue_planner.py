import uuid
from typing import Dict, Any, List
from app.models.audio import DialogueSegment

class DialoguePlannerService:
    @staticmethod
    def plan_dialogue_for_scene(
        scene_storyboard: Dict[str, Any],
        scene_number: int
    ) -> List[DialogueSegment]:
        narration = scene_storyboard.get("narration_text", "Once upon a time in a colorful dinosaur valley...")
        visual_plan = scene_storyboard.get("visual_plan", {})
        mood = visual_plan.get("mood", "Cheerful")
        
        # Split narration into sentences
        sentences = [s.strip() for s in narration.replace("!", ".").replace("?", ".").split(".") if s.strip()]
        if not sentences:
            sentences = [narration]

        segments: List[DialogueSegment] = []
        for idx, sentence in enumerate(sentences, 1):
            # Extract potential emphasis words (longer words)
            words = [w.strip(",.") for w in sentence.split() if len(w) > 4]
            emphasis = words[:2] if words else []

            seg = DialogueSegment(
                segment_id=f"seg_s{scene_number}_{idx}_{uuid.uuid4().hex[:4]}",
                scene_number=scene_number,
                speaker_name="Narrator",
                speaker_role="Narrator",
                text=sentence,
                emotional_tone=mood,
                speech_speed=1.0,
                pause_duration_seconds=0.3,
                emphasis_words=emphasis
            )
            segments.append(seg)

        return segments
