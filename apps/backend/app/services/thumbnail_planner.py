import uuid
from typing import Dict, Any, List
from app.models.publishing import ThumbnailVariant

class ThumbnailPlannerService:
    @staticmethod
    def plan_thumbnail_variants(storyboard: Dict[str, Any], project_title: str) -> List[ThumbnailVariant]:
        scenes = storyboard.get("scenes", [])
        visual_style = storyboard.get("visual_style", "3D Pixar Render")
        base_prompt = scenes[0].get("narration_text", project_title) if scenes else project_title

        sample_thumb_url = "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=800&auto=format&fit=crop&q=80"

        variants = [
            ThumbnailVariant(
                variant_id=f"thm_a_{uuid.uuid4().hex[:6]}",
                version_name="Version A",
                style_type="Character Focus",
                prompt=f"Expressive character closeup, joyful face, bright studio lighting, {visual_style}, high contrast, 16:9 thumbnail --ar 16:9",
                storage_url=sample_thumb_url,
                ctr_score=94.5,
                selected=True
            ),
            ThumbnailVariant(
                variant_id=f"thm_b_{uuid.uuid4().hex[:6]}",
                version_name="Version B",
                style_type="Action Scene",
                prompt=f"Dynamic action composition, main character jumping in lush environment, dramatic camera angle, {visual_style} --ar 16:9",
                storage_url=sample_thumb_url,
                ctr_score=91.0,
                selected=False
            ),
            ThumbnailVariant(
                variant_id=f"thm_c_{uuid.uuid4().hex[:6]}",
                version_name="Version C",
                style_type="Bright Cartoon",
                prompt=f"Super bright vibrant colors, cute 3D cartoon style, high saturation, playful atmosphere, {visual_style} --ar 16:9",
                storage_url=sample_thumb_url,
                ctr_score=89.5,
                selected=False
            ),
            ThumbnailVariant(
                variant_id=f"thm_d_{uuid.uuid4().hex[:6]}",
                version_name="Version D",
                style_type="Educational Style",
                prompt=f"Main character pointing at colorful educational object, clear visual hierarchy, Pixar 3D style --ar 16:9",
                storage_url=sample_thumb_url,
                ctr_score=93.0,
                selected=False
            )
        ]
        return variants
