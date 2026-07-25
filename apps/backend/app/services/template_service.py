import uuid
from typing import Dict, List
from app.models.copilot import ContentTemplateItem

templates_db: Dict[str, ContentTemplateItem] = {}

class TemplateService:
    @staticmethod
    def initialize_default_templates():
        if not templates_db:
            t1 = ContentTemplateItem(
                template_id="tmpl_001",
                name="3D Pixar Dinosaur Adventure",
                category="STORY",
                description="High-converting educational template featuring Baby Dinosaur exploring prehistoric nature.",
                tags=["dinosaur", "3d pixar", "kids learning"],
                payload={"target_age": "3-5", "video_style": "3D Pixar Render", "scenes_count": 4},
                downloads_count=142
            )
            t2 = ContentTemplateItem(
                template_id="tmpl_002",
                name="High-CTR Character Closeup Thumbnail",
                category="THUMBNAIL",
                description="CTR-optimized thumbnail setup with expressive character closeup and bright gradient backdrop.",
                tags=["thumbnail", "high ctr", "3d character"],
                payload={"contrast": "high", "lighting": "studio", "style": "Version A"},
                downloads_count=98
            )
            templates_db[t1.template_id] = t1
            templates_db[t2.template_id] = t2

    @staticmethod
    def list_templates() -> List[ContentTemplateItem]:
        TemplateService.initialize_default_templates()
        return list(templates_db.values())

    @staticmethod
    def create_template(name: str, category: str, description: str, tags: List[str], payload: Dict) -> ContentTemplateItem:
        tmpl = ContentTemplateItem(
            template_id=f"tmpl_{uuid.uuid4().hex[:6]}",
            name=name,
            category=category,
            description=description,
            tags=tags,
            payload=payload,
            downloads_count=0
        )
        templates_db[tmpl.template_id] = tmpl
        return tmpl
