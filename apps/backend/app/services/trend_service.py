from typing import List
from app.models.copilot import TrendReport

class TrendService:
    @staticmethod
    def get_trending_topics() -> List[TrendReport]:
        return [
            TrendReport(
                trend_id="tr_001",
                topic="Dinosaurs & Prehistoric Earth",
                category="SCIENCE",
                search_volume_score=98.5,
                competition_level="MEDIUM",
                opportunity_score=95.0,
                target_age_group="3-5",
                seasonal_keywords=["baby dino", "dinosaur sounds", "prehistoric kids"]
            ),
            TrendReport(
                trend_id="tr_002",
                topic="Solar System & Space Adventure",
                category="SCIENCE",
                search_volume_score=92.0,
                competition_level="LOW",
                opportunity_score=94.5,
                target_age_group="5-8",
                seasonal_keywords=["planets for kids", "rocket ship", "astronaut adventure"]
            ),
            TrendReport(
                trend_id="tr_003",
                topic="Underwater Sea Animals & Coral Reefs",
                category="ANIMALS",
                search_volume_score=88.0,
                competition_level="LOW",
                opportunity_score=91.0,
                target_age_group="3-5",
                seasonal_keywords=["ocean life", "baby shark learning", "sea creatures"]
            )
        ]
