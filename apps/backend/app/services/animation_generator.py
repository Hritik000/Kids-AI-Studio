import uuid
import time
from typing import List, Dict, Any, Optional
from app.models.animation import AnimatedSceneClip, MotionPlan
from app.core.animation_provider import get_animation_provider, AnimationProvider
from app.services.motion_planner import MotionPlannerService
from app.services.animation_validator import AnimationValidationService, AnimationValidationError
from app.core.llm import PromptLoader

# In-memory repository for Animated Scene Clips
animations_db: Dict[str, List[AnimatedSceneClip]] = {}

class AnimationPipelineService:
    def __init__(self, animation_provider: Optional[AnimationProvider] = None):
        self.provider = animation_provider or get_animation_provider()

    async def generate_all_scene_animations(
        self,
        project_id: str,
        storyboard: Dict[str, Any],
        scene_images: List[Any],
        characters: List[Any]
    ) -> List[AnimatedSceneClip]:
        scenes = storyboard.get("scenes", [])
        generated_clips: List[AnimatedSceneClip] = []

        for idx, scene in enumerate(scenes, 1):
            scene_num = scene.get("scene_number", idx)
            matched_img = next((img for img in scene_images if getattr(img, "scene_number", None) == scene_num or (isinstance(img, dict) and img.get("scene_number") == scene_num)), None)
            
            image_url = getattr(matched_img, "storage_url", None) if matched_img else f"https://placehold.co/1280x720/1A1D27/FFFFFF/png?text=Scene+{scene_num}"

            # 1. Generate Motion Plan
            motion_plan = MotionPlannerService.plan_motion_for_scene(scene, characters)

            # 2. Compose Motion Prompt
            primary_char_name = scene.get("character_references", [{}])[0].get("character_name", "Rexy") if scene.get("character_references") else "Hero"
            env_name = scene.get("visual_plan", {}).get("environment", "Meadow")

            composed_motion_prompt = PromptLoader.load_prompt("animation.md", {
                "character_name": primary_char_name,
                "environment": env_name,
                "camera_path": motion_plan.camera_path,
                "camera_speed": motion_plan.camera_speed,
                "character_motion": motion_plan.character_motion,
                "environment_motion": motion_plan.environment_motion
            })

            seed = 100 + scene_num
            start_time = time.time()

            raw_output = await self.provider.generate_animation_clip(
                image_url=image_url,
                motion_prompt=composed_motion_prompt,
                duration_seconds=motion_plan.duration_seconds,
                width=1280,
                height=720,
                seed=seed
            )
            duration = round(time.time() - start_time, 2)

            clip_record = AnimatedSceneClip(
                animation_id=f"anim_{project_id}_{scene_num}_{uuid.uuid4().hex[:6]}",
                project_id=project_id,
                scene_number=scene_num,
                motion_plan=motion_plan,
                composed_motion_prompt=composed_motion_prompt,
                provider=raw_output.get("provider", "Wan2.2-i2v"),
                seed=seed,
                duration_seconds=motion_plan.duration_seconds,
                frame_rate=24,
                generation_time_seconds=duration,
                status="GENERATED",
                storage_url=raw_output["storage_url"],
                thumbnail_url=raw_output["thumbnail_url"]
            )

            # Validate Clip Record
            AnimationValidationService.validate_animation(clip_record.model_dump())
            generated_clips.append(clip_record)

        animations_db[project_id] = generated_clips
        return generated_clips

    async def regenerate_single_scene_animation(
        self,
        project_id: str,
        scene_number: int,
        storyboard: Dict[str, Any],
        scene_images: List[Any],
        characters: List[Any]
    ) -> AnimatedSceneClip:
        existing_clips = animations_db.get(project_id, [])
        scenes = storyboard.get("scenes", [])
        scene = next((s for s in scenes if s.get("scene_number") == scene_number), {})
        
        matched_img = next((img for img in scene_images if getattr(img, "scene_number", None) == scene_number), None)
        image_url = getattr(matched_img, "storage_url", None) if matched_img else f"https://placehold.co/1280x720/1A1D27/FFFFFF/png?text=Scene+{scene_number}"

        motion_plan = MotionPlannerService.plan_motion_for_scene(scene, characters)
        primary_char_name = scene.get("character_references", [{}])[0].get("character_name", "Hero") if scene.get("character_references") else "Hero"
        env_name = scene.get("visual_plan", {}).get("environment", "Meadow")

        composed_motion_prompt = PromptLoader.load_prompt("animation.md", {
            "character_name": primary_char_name,
            "environment": env_name,
            "camera_path": motion_plan.camera_path,
            "camera_speed": motion_plan.camera_speed,
            "character_motion": motion_plan.character_motion,
            "environment_motion": motion_plan.environment_motion
        })

        new_seed = int(time.time() * 1000) % 100000
        start_time = time.time()

        raw_output = await self.provider.generate_animation_clip(
            image_url=image_url,
            motion_prompt=composed_motion_prompt,
            duration_seconds=motion_plan.duration_seconds,
            width=1280,
            height=720,
            seed=new_seed
        )
        duration = round(time.time() - start_time, 2)

        new_clip = AnimatedSceneClip(
            animation_id=f"anim_{project_id}_{scene_number}_{uuid.uuid4().hex[:6]}",
            project_id=project_id,
            scene_number=scene_number,
            motion_plan=motion_plan,
            composed_motion_prompt=composed_motion_prompt,
            provider=raw_output.get("provider", "Wan2.2-i2v"),
            seed=new_seed,
            duration_seconds=motion_plan.duration_seconds,
            frame_rate=24,
            generation_time_seconds=duration,
            status="GENERATED",
            storage_url=raw_output["storage_url"],
            thumbnail_url=raw_output["thumbnail_url"]
        )

        updated_list = [clip for clip in existing_clips if clip.scene_number != scene_number]
        updated_list.append(new_clip)
        updated_list.sort(key=lambda x: x.scene_number)
        animations_db[project_id] = updated_list

        return new_clip
