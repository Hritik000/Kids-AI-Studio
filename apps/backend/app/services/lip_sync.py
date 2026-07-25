from typing import List
from app.models.audio import DialogueSegment, LipSyncMetadata, VisemeMarker

class LipSyncEngineService:
    @staticmethod
    def generate_lip_sync_timeline(
        segments: List[DialogueSegment],
        total_duration: float = 5.0
    ) -> LipSyncMetadata:
        visemes: List[VisemeMarker] = []
        current_time = 0.2
        mouth_shapes = ["A", "E", "O", "I", "U", "M", "Rest"]

        for seg in segments:
            words = seg.text.split()
            for idx, word in enumerate(words):
                shape = mouth_shapes[idx % (len(mouth_shapes) - 1)]
                dur = round(0.12 + (len(word) * 0.02), 2)
                
                visemes.append(VisemeMarker(
                    timestamp_seconds=round(current_time, 2),
                    mouth_shape=shape,
                    duration_seconds=dur
                ))
                current_time += dur

            # Add rest pause
            current_time += seg.pause_duration_seconds
            visemes.append(VisemeMarker(
                timestamp_seconds=round(current_time, 2),
                mouth_shape="Rest",
                duration_seconds=0.2
            ))

        # Blink timestamps every 2.5 seconds
        blinks = [round(b, 1) for b in [1.5, 4.0, 6.5] if b < total_duration]

        return LipSyncMetadata(
            visemes=visemes,
            blink_timestamps=blinks
        )
