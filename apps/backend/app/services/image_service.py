from typing import List
from app.models.project import Scene
from app.core.adapters.image_adapter import image_adapter

class ImageService:
    async def generate_scene_images(self, scenes: List[Scene]) -> List[Scene]:
        updated_scenes = []
        for scene in scenes:
            image_url = await image_adapter.generate_image(scene.visual_prompt, scene.scene_number)
            scene.image_url = image_url
            updated_scenes.append(scene)
        return updated_scenes

image_service = ImageService()
