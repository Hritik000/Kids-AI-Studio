import uuid
from typing import Dict, Any, List, Optional
from app.models.publishing import SEOPackage, TitleOption, ChapterItem
from app.core.llm import PromptLoader

class SEOAgentService:
    @staticmethod
    def generate_seo_package(
        project_id: str,
        project_title: str,
        prompt: str,
        story_script: Optional[Dict[str, Any]] = None
    ) -> SEOPackage:
        # Load prompt templates
        title_prompt = PromptLoader.load_prompt("title.md", {"title": project_title})
        desc_prompt = PromptLoader.load_prompt("description.md", {"title": project_title})

        title_1 = f"Fun Learning: {project_title} | Educational Cartoons for Kids"
        title_2 = f"What Happens When {project_title}? 🦕 Learn & Play!"
        title_3 = f"Learn {project_title} - Story Time for Toddlers & Preschoolers"

        title_options = [
            TitleOption(
                title_id=f"ttl_{uuid.uuid4().hex[:6]}",
                title_text=title_1,
                category="SEO Optimized",
                ctr_score=96.0,
                character_count=len(title_1)
            ),
            TitleOption(
                title_id=f"ttl_{uuid.uuid4().hex[:6]}",
                title_text=title_2,
                category="Curiosity Driven",
                ctr_score=92.5,
                character_count=len(title_2)
            ),
            TitleOption(
                title_id=f"ttl_{uuid.uuid4().hex[:6]}",
                title_text=title_3,
                category="Educational",
                ctr_score=94.0,
                character_count=len(title_3)
            )
        ]

        chapters = [
            ChapterItem(timestamp="00:00", title="Introduction & Story Start", summary="Meet the characters!"),
            ChapterItem(timestamp="00:45", title="Fun Discovery & Lesson", summary="Educational activity scene"),
            ChapterItem(timestamp="01:30", title="Celebration & Conclusion", summary="Singalong ending")
        ]

        long_desc = (
            f"Join us for an exciting educational adventure with '{project_title}'! Designed for kids ages 3-5.\n\n"
            "CHAPTERS:\n"
            "00:00 - Introduction & Story Start\n"
            "00:45 - Fun Discovery & Lesson\n"
            "01:30 - Singalong Ending\n\n"
            "Subscribe to KidsAI Studio for new 3D animated learning videos every week!"
        )

        return SEOPackage(
            seo_id=f"seo_{project_id}_{uuid.uuid4().hex[:6]}",
            project_id=project_id,
            selected_title=title_1,
            title_options=title_options,
            short_description=f"Fun educational story about {project_title} for kids and toddlers!",
            long_description=long_desc,
            chapters=chapters,
            primary_keywords=["kids learning", "educational cartoon", "preschool learning", "toddler stories"],
            secondary_keywords=["3D animation for kids", "storytime for toddlers", "fun learning video"],
            hashtags=["#KidsAI", "#KidsLearning", "#CartoonsForKids", "#PreschoolLearning", "#Storytime"],
            category="Education",
            coppa_compliant=True
        )
