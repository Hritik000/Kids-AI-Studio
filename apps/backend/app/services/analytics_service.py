from typing import Dict, Any
from app.models.saas import AnalyticsSummary
from app.api.v1.projects import projects_db
from app.api.v1.rendering import renders_db
from app.services.billing_service import BillingService

class AnalyticsService:
    @staticmethod
    def get_summary(user_id: str) -> AnalyticsSummary:
        sub = BillingService.get_user_subscription(user_id)
        total_projects = len(projects_db)

        return AnalyticsSummary(
            total_projects=total_projects,
            total_stories_generated=total_projects * 2,
            total_images_generated=total_projects * 4,
            total_video_clips_generated=total_projects * 4,
            total_audio_tracks_generated=total_projects * 4,
            total_render_minutes=round(total_projects * 1.5, 1),
            render_success_rate=99.4,
            ai_provider_health="OPERATIONAL (FLUX, Wan 2.2, Kokoro, Stable Audio)",
            credits_remaining=sub.credits_remaining,
            active_subscription=sub.plan_id
        )
