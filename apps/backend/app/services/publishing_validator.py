from typing import Dict, Any

class PublishingValidationError(Exception):
    pass

class PublishingValidatorService:
    @staticmethod
    def validate_publishing_bundle(bundle_data: Dict[str, Any]) -> None:
        required = ["bundle_id", "project_id", "thumbnails", "seo"]
        for key in required:
            if key not in bundle_data or bundle_data[key] is None:
                raise PublishingValidationError(f"Publishing bundle missing required field: '{key}'")

        thumbnails = bundle_data.get("thumbnails", [])
        if not isinstance(thumbnails, list) or len(thumbnails) < 1:
            raise PublishingValidationError("At least 1 thumbnail variant is required.")

        for thumb in thumbnails:
            if not thumb.get("storage_url", "").startswith("http"):
                raise PublishingValidationError(f"Invalid thumbnail URL format: '{thumb.get('storage_url')}'")

        seo = bundle_data.get("seo", {})
        if not seo.get("selected_title"):
            raise PublishingValidationError("SEO package must contain a selected title.")
        if len(seo["selected_title"]) > 100:
            raise PublishingValidationError(f"Title exceeds 100 character limit ({len(seo['selected_title'])} chars).")
