from typing import Dict, Any, List

class TransitionEngineService:
    @staticmethod
    def get_supported_transitions() -> List[str]:
        return ["Cut", "Fade", "CrossFade", "Dissolve", "Zoom", "Slide", "Whip", "Blur", "Flash"]

    @staticmethod
    def calculate_transition_offset(scene_duration: float, transition_duration: float = 0.5) -> Dict[str, float]:
        return {
            "start_time": max(0.0, scene_duration - transition_duration),
            "duration": transition_duration
        }
