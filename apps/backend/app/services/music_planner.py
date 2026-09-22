import uuid
from typing import Dict, Any, List, Optional
from app.models.music import MusicPlan

class MusicPlannerService:
    @staticmethod
    def plan_music_for_project(
        storyboard: Dict[str, Any],
        production_plan: Optional[Dict[str, Any]] = None
    ) -> MusicPlan:
        visual_style = storyboard.get("visual_style", "3D Pixar Render")
        total_duration = float(storyboard.get("total_duration_seconds", 60.0))
        scenes = storyboard.get("scenes", [])
        
        mood = scenes[0].get("visual_plan", {}).get("mood", "Cheerful & Adventurous") if scenes else "Cheerful"

        return MusicPlan(
            track_id=f"mus_{uuid.uuid4().hex[:6]}",
            genre="Child-Friendly Acoustic Orchestral",
            mood=mood,
            bpm=112,
            key="C Major",
            instruments=["Marimba", "Acoustic Guitar", "Pizzicato Strings", "Flute"],
            duration_seconds=total_duration,
            loop_enabled=True
        )
