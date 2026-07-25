from typing import Dict, Any

class DistributionValidationError(Exception):
    pass

class DistributionValidatorService:
    @staticmethod
    def validate_publish_request(video_url: str, title: str, platform: str) -> None:
        if not video_url or not video_url.startswith("http"):
            raise DistributionValidationError("Valid video URL is required before publishing.")

        if not title:
            raise DistributionValidationError("Title is required before publishing.")

        if len(title) > 100 and "YOUTUBE" in platform.upper():
            raise DistributionValidationError(f"YouTube titles cannot exceed 100 characters ({len(title)} given).")
