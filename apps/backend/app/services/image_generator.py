import uuid
import time
from typing import List, Dict, Any, Optional
from app.models.character import GeneratedImage, CharacterProfile
from app.core.image_provider import get_image_provider, ImageProvider
from app.services.prompt_composer import PromptComposerService
from app.services.image_validator import ImageValidationService, ImageValidationError

# In-memory repository for Generated Images
images_db: Dict[str, List[GeneratedImage]] = {}

class ImagePipelineService:
    def __init__(self, image_provider: Optional[ImageProvider] = None):
        self.provider = image_provider or get_image_provider()

    async def generate_all_scene_images(
        self,
        project_id: str,
        storyboard: Dict[str, Any],
        characters: List[CharacterProfile]
    ) -> List[GeneratedImage]:
        scenes = storyboard.get("scenes", [])
        visual_style = storyboard.get("visual_style", "3D Pixar Render")
        generated_list: List[GeneratedImage] = []

        for idx, scene in enumerate(scenes, 1):
            scene_num = scene.get("scene_number", idx)
            
            # Compose Prompt
            prompts = PromptComposerService.compose_scene_prompt(
                scene_storyboard=scene,
                characters=characters,
                visual_style=visual_style
            )

            seed = 42 + scene_num
            start_time = time.time()
            
            raw_output = await self.provider.generate_image(
                prompt=prompts["positive_prompt"],
                negative_prompt=prompts["negative_prompt"],
                width=1280,
                height=720,
                seed=seed
            )
            duration = round(time.time() - start_time, 2)

            img_record = GeneratedImage(
                image_id=f"img_{project_id}_{scene_num}_{uuid.uuid4().hex[:6]}",
                project_id=project_id,
                scene_number=scene_num,
                composed_prompt=prompts["positive_prompt"],
                negative_prompt=prompts["negative_prompt"],
                provider=raw_output.get("provider", "FLUX-v1"),
                seed=seed,
                generation_time_seconds=duration,
                status="GENERATED",
                storage_url=raw_output["storage_url"],
                thumbnail_url=raw_output["thumbnail_url"]
            )

            # Validate Image Record
            ImageValidationService.validate_image(img_record.model_dump())
            generated_list.append(img_record)

        images_db[project_id] = generated_list
        return generated_list

    async def regenerate_single_scene_image(
        self,
        project_id: str,
        scene_number: int,
        storyboard: Dict[str, Any],
        characters: List[CharacterProfile]
    ) -> GeneratedImage:
        existing_list = images_db.get(project_id, [])
        scenes = storyboard.get("scenes", [])
        scene = next((s for s in scenes if s.get("scene_number") == scene_number), {})
        visual_style = storyboard.get("visual_style", "3D Pixar Render")

        prompts = PromptComposerService.compose_scene_prompt(
            scene_storyboard=scene,
            characters=characters,
            visual_style=visual_style
        )

        new_seed = int(time.time() * 1000) % 100000
        start_time = time.time()

        raw_output = await self.provider.generate_image(
            prompt=prompts["positive_prompt"],
            negative_prompt=prompts["negative_prompt"],
            width=1280,
            height=720,
            seed=new_seed
        )
        duration = round(time.time() - start_time, 2)

        new_img = GeneratedImage(
            image_id=f"img_{project_id}_{scene_number}_{uuid.uuid4().hex[:6]}",
            project_id=project_id,
            scene_number=scene_number,
            composed_prompt=prompts["positive_prompt"],
            negative_prompt=prompts["negative_prompt"],
            provider=raw_output.get("provider", "FLUX-v1"),
            seed=new_seed,
            generation_time_seconds=duration,
            status="GENERATED",
            storage_url=raw_output["storage_url"],
            thumbnail_url=raw_output["thumbnail_url"]
        )

        # Replace in repository list
        updated_list = [img for img in existing_list if img.scene_number != scene_number]
        updated_list.append(new_img)
        updated_list.sort(key=lambda x: x.scene_number)
        images_db[project_id] = updated_list

        return new_img
