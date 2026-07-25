import uuid
from typing import Dict, Any, List
from app.models.copilot import OptimizationReport, OptimizationSuggestion

optimization_reports_db: Dict[str, OptimizationReport] = {}

class CreatorCopilotService:
    @staticmethod
    def analyze_project(project_id: str, title: str, prompt: str, scene_count: int = 4) -> OptimizationReport:
        suggestions = [
            OptimizationSuggestion(
                category="TITLE",
                severity="MEDIUM",
                current_value=title,
                suggested_value=f"Fun Learning: {title} | Educational Cartoons for Kids",
                explanation="Adding clear benefit keywords ('Educational', 'Fun Learning') boosts click-through rate by up to 35%."
            ),
            OptimizationSuggestion(
                category="PACING",
                severity="LOW",
                current_value=f"{scene_count} scenes",
                suggested_value="Maintain 4.5s average scene duration",
                explanation="Kids aged 3-5 maintain peak attention when visual scene cuts occur every 4-5 seconds."
            ),
            OptimizationSuggestion(
                category="THUMBNAIL",
                severity="HIGH",
                current_value="Standard render",
                suggested_value="Use Version A (Character Focus with High Contrast)",
                explanation="Close-up character facial expressions increase mobile thumbnail CTR significantly."
            )
        ]

        report = OptimizationReport(
            project_id=project_id,
            overall_score=92.5,
            pacing_score=94.0,
            educational_score=96.0,
            visual_score=90.0,
            audio_score=90.0,
            strengths=[
                "Strong educational narrative with clear call-to-action",
                "High visual continuity across 3D Pixar characters",
                "LUFS mastered audio with speech ducking"
            ],
            weaknesses=[
                "Title could be more curiosity-driven for YouTube Kids algorithm"
            ],
            suggestions=suggestions
        )
        optimization_reports_db[project_id] = report
        return report

    @staticmethod
    def optimize_prompt(raw_prompt: str) -> Dict[str, Any]:
        enhanced = f"Masterpiece 3D Pixar Render, vibrant lighting, highly detailed kids animation: {raw_prompt}, 8k resolution, child-friendly color palette"
        return {
            "original_prompt": raw_prompt,
            "optimized_prompt": enhanced,
            "quality_score": 95.0,
            "improvements": ["Added 3D Pixar lighting tokens", "Enforced child-friendly color palette constraint"]
        }
