import uuid
from typing import Dict, Any, List, Optional
from app.models.publishing import PublishingAssetBundle, ThumbnailVariant, SEOPackage
from app.services.thumbnail_planner import ThumbnailPlannerService
from app.services.seo_agent import SEOAgentService
from app.services.publishing_validator import PublishingValidatorService, PublishingValidationError

# In-memory database for publishing asset bundles
publishing_bundles_db: Dict[str, PublishingAssetBundle] = {}

class PublishingPipelineService:
    @staticmethod
    def generate_publishing_assets(
        project_id: str,
        project_title: str,
        prompt: str,
        storyboard: Dict[str, Any],
        story_script: Optional[Dict[str, Any]] = None
    ) -> PublishingAssetBundle:
        thumbnails = ThumbnailPlannerService.plan_thumbnail_variants(storyboard, project_title)
        seo_package = SEOAgentService.generate_seo_package(project_id, project_title, prompt, story_script)

        bundle = PublishingAssetBundle(
            bundle_id=f"pub_{project_id}_{uuid.uuid4().hex[:6]}",
            project_id=project_id,
            thumbnails=thumbnails,
            seo=seo_package,
            status="GENERATED"
        )

        PublishingValidatorService.validate_publishing_bundle(bundle.model_dump())
        publishing_bundles_db[project_id] = bundle
        return bundle

    @staticmethod
    def select_thumbnail_variant(project_id: str, variant_id: str) -> ThumbnailVariant:
        bundle = publishing_bundles_db.get(project_id)
        if not bundle:
            raise PublishingValidationError("Publishing asset bundle not found")

        selected_variant = None
        for thumb in bundle.thumbnails:
            if thumb.variant_id == variant_id:
                thumb.selected = True
                selected_variant = thumb
            else:
                thumb.selected = False

        if not selected_variant:
            raise PublishingValidationError(f"Thumbnail variant '{variant_id}' not found.")

        publishing_bundles_db[project_id] = bundle
        return selected_variant
