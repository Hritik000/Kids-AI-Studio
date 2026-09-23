"""
Production-Correct, Provider-Agnostic Image Generation Layer.
Provides clean ImageProvider abstraction for Replicate FLUX models and Mock providers.
Features Replicate async prediction lifecycle, status polling, image validation,
local persistent asset storage, and secret masking.
"""

import os
import time
import re
import urllib.parse
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import httpx
from app.core.config import settings
from datetime import datetime, timezone

logger = logging.getLogger("image_provider")


class ImageProviderError(Exception):
    """Base exception for all image provider errors."""
    pass


class ImageConfigurationError(ImageProviderError):
    """Raised when Image Provider configuration or API key is missing in real mode."""
    pass


class ImageAuthError(ImageProviderError):
    """Raised when authentication fails (HTTP 401/403)."""
    pass


class ImageRateLimitError(ImageProviderError):
    """Raised when rate limit is hit (HTTP 429)."""
    pass


class ImageTimeoutError(ImageProviderError):
    """Raised when image generation or status polling times out."""
    pass


class ImageAPIError(ImageProviderError):
    """Raised when generic HTTP or provider API error occurs."""
    pass


def mask_secret(text: str, secret: Optional[str] = None) -> str:
    """Masks secret API keys in log messages and error tracebacks."""
    if not text:
        return text
    secrets_to_mask = [secret] if secret else []
    for key_env in ["REPLICATE_API_KEY", "FLUX_API_KEY", "IMAGE_API_KEY"]:
        val = os.getenv(key_env) or getattr(settings, key_env, "")
        if val:
            secrets_to_mask.append(val)

    masked_text = str(text)
    for s in secrets_to_mask:
        if s and len(s) > 4:
            masked = f"{s[:3]}...{s[-4:]}"
            masked_text = masked_text.replace(s, masked)
    return masked_text


class ImageProvider(ABC):
    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1280,
        height: int = 720,
        seed: int = 42,
        project_id: str = "default_project"
    ) -> Dict[str, Any]:
        """Generates an image and returns metadata with local/storage asset URL."""
        pass


class MockImageProvider(ImageProvider):
    """
    Deterministic Mock Image Provider for automated unit tests and keyless local development.
    """

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1280,
        height: int = 720,
        seed: int = 42,
        project_id: str = "default_project"
    ) -> Dict[str, Any]:
        short_prompt = prompt[:45].replace(" ", "+")
        encoded = urllib.parse.quote(short_prompt)
        image_url = f"https://placehold.co/{width}x{height}/1A1D27/FFFFFF/png?text={encoded}"
        thumb_url = f"https://placehold.co/400x225/1A1D27/FFFFFF/png?text={encoded}"

        return {
            "provider": "FLUX-v1-Mock",
            "seed": seed,
            "width": width,
            "height": height,
            "storage_url": image_url,
            "thumbnail_url": thumb_url
        }


class FluxImageProvider(ImageProvider):
    """
    Production-grade Image Provider communicating with Replicate FLUX models.
    Handles prediction creation, bounded polling loop, status checking (starting -> processing -> succeeded),
    image validation, and local asset persistence.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        poll_interval: Optional[float] = None,
        timeout_seconds: Optional[float] = None
    ):
        self.api_key = api_key or getattr(settings, "REPLICATE_API_KEY", "") or os.getenv("REPLICATE_API_KEY") or os.getenv("FLUX_API_KEY") or os.getenv("IMAGE_API_KEY") or ""
        self.model = model or getattr(settings, "IMAGE_MODEL", "black-forest-labs/flux-schnell") or "black-forest-labs/flux-schnell"
        self.poll_interval = poll_interval or getattr(settings, "IMAGE_POLL_INTERVAL", 1.0) or 1.0
        self.timeout_seconds = timeout_seconds or getattr(settings, "IMAGE_TIMEOUT", 60.0) or 60.0

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1280,
        height: int = 720,
        seed: int = 42,
        project_id: str = "default_project"
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise ImageConfigurationError(
                "Replicate API key is missing. Set REPLICATE_API_KEY or set IMAGE_PROVIDER=mock for development/testing."
            )

        # Build Replicate Prediction Creation Endpoint
        if "/" in self.model:
            create_url = f"https://api.replicate.com/v1/models/{self.model}/predictions"
            body: Dict[str, Any] = {
                "input": {
                    "prompt": prompt,
                    "aspect_ratio": "16:9",
                    "seed": seed
                }
            }
        else:
            create_url = "https://api.replicate.com/v1/predictions"
            body = {
                "version": self.model,
                "input": {
                    "prompt": prompt,
                    "aspect_ratio": "16:9",
                    "seed": seed
                }
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Prefer": "wait"
        }

        logger.info("Submitting Replicate image prediction request for model %s...", self.model)

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            # 1. Create Prediction Request
            try:
                resp = await client.post(create_url, headers=headers, json=body)
            except (httpx.TimeoutException, asyncio.TimeoutError) as e:
                raise ImageTimeoutError(f"Replicate API initial POST request timed out after {self.timeout_seconds}s") from e
            except Exception as e:
                raise ImageAPIError(f"Failed to submit Replicate prediction: {mask_secret(str(e), self.api_key)}") from e

            if resp.status_code in (401, 403):
                err_text = mask_secret(resp.text, self.api_key)
                raise ImageAuthError(f"Replicate API Authentication failed (HTTP {resp.status_code}): {err_text}")

            if resp.status_code == 429:
                err_text = mask_secret(resp.text, self.api_key)
                raise ImageRateLimitError(f"Replicate API Rate Limit exceeded (HTTP 429): {err_text}")

            if resp.status_code >= 500:
                err_text = mask_secret(resp.text, self.api_key)
                raise ImageAPIError(f"Replicate Server Error (HTTP {resp.status_code}): {err_text}")

            if resp.status_code >= 400:
                err_text = mask_secret(resp.text, self.api_key)
                raise ImageAPIError(f"Replicate API Request Error (HTTP {resp.status_code}): {err_text}")

            data = resp.json()
            prediction_id = data.get("id")
            status = data.get("status")
            poll_url = data.get("urls", {}).get("get") or f"https://api.replicate.com/v1/predictions/{prediction_id}"

            # 2. Bounded Polling Loop if prediction is starting or processing
            if status in ("starting", "processing"):
                logger.info("Prediction %s status: %s. Starting polling loop (interval: %.1fs, timeout: %.1fs)...", prediction_id, status, self.poll_interval, self.timeout_seconds)
                start_poll = time.time()

                while time.time() - start_poll < self.timeout_seconds:
                    await asyncio.sleep(self.poll_interval)
                    try:
                        poll_resp = await client.get(poll_url, headers=headers)
                    except Exception as e:
                        logger.warning("Polling error for prediction %s: %s", prediction_id, mask_secret(str(e), self.api_key))
                        continue

                    if poll_resp.status_code == 429:
                        logger.warning("Rate limited during status polling (HTTP 429). Waiting...")
                        await asyncio.sleep(2.0)
                        continue

                    if poll_resp.status_code >= 400:
                        err_text = mask_secret(poll_resp.text, self.api_key)
                        raise ImageAPIError(f"Error polling prediction status (HTTP {poll_resp.status_code}): {err_text}")

                    poll_data = poll_resp.json()
                    status = poll_data.get("status")

                    if status == "succeeded":
                        data = poll_data
                        logger.info("Prediction %s succeeded!", prediction_id)
                        break
                    elif status == "failed":
                        err_msg = poll_data.get("error") or "Unknown prediction failure error"
                        raise ImageAPIError(f"Replicate image generation failed for prediction {prediction_id}: {err_msg}")
                    elif status == "canceled":
                        raise ImageAPIError(f"Replicate image generation was canceled for prediction {prediction_id}.")
                else:
                    raise ImageTimeoutError(f"Replicate image generation timed out after {self.timeout_seconds}s for prediction {prediction_id}")

            if status == "failed":
                err_msg = data.get("error") or "Unknown error"
                raise ImageAPIError(f"Replicate image generation failed: {err_msg}")

            if status == "canceled":
                raise ImageAPIError("Replicate image generation was canceled.")

            if status != "succeeded":
                raise ImageAPIError(f"Unexpected Replicate prediction status: {status}")

            # 3. Extract Output URL
            output = data.get("output")
            if isinstance(output, list) and len(output) > 0:
                raw_output_url = output[0]
            elif isinstance(output, str):
                raw_output_url = output
            else:
                raise ImageAPIError(f"Replicate prediction {prediction_id} missing valid output image URL.")

            if not raw_output_url or not isinstance(raw_output_url, str) or not raw_output_url.startswith("http"):
                raise ImageAPIError(f"Invalid image output URL returned by Replicate: {raw_output_url}")

            # 4. Download and Persist Image Asset locally using MediaDownloader
            from app.services.rendering.downloader import MediaDownloader
            try:
                local_asset_path = MediaDownloader.download_asset(raw_output_url, project_id=project_id)
            except Exception as e:
                raise ImageAPIError(f"Failed to download and persist generated image from {raw_output_url}: {str(e)}") from e

            # Validate downloaded asset file
            if not os.path.isfile(local_asset_path):
                raise ImageAPIError(f"Downloaded image file does not exist at '{local_asset_path}'")

            file_size = os.path.getsize(local_asset_path)
            if file_size == 0:
                raise ImageAPIError(f"Downloaded image file is empty (0 bytes) at '{local_asset_path}'")

            ext = os.path.splitext(local_asset_path)[1].lower()
            if ext not in (".png", ".jpg", ".jpeg", ".webp", ".gif"):
                raise ImageAPIError(f"Downloaded asset has non-image extension '{ext}' at '{local_asset_path}'")

            logger.info("Successfully generated and persisted real image asset: %s (%d bytes)", local_asset_path, file_size)

            return {
                "provider": f"FLUX-Replicate ({self.model})",
                "seed": seed,
                "width": width,
                "height": height,
                "storage_url": local_asset_path,
                "thumbnail_url": local_asset_path
            }



class PollinationsImageProvider(ImageProvider):
    """Free unlimited image generation via Pollinations AI"""

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1280,
        height: int = 720,
        seed: int = 42,
        project_id: str = "default_project"
    ) -> Dict[str, Any]:
        import hashlib
        from pathlib import Path
        import urllib.parse

        # URL-encode the prompt for Pollinations
        encoded_prompt = urllib.parse.quote_plus(prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&private=true"

        # Prepare local storage path
        assets_dir = Path("/tmp/kidsai_renders") / project_id / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)

        # Generate deterministic filename
        hash_input = f"{prompt}{negative_prompt}{width}{height}{seed}"
        file_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
        local_path = assets_dir / f"asset_{file_hash}.png"

        # Download image
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(image_url)
            if resp.status_code == 200:
                image_data = resp.content
                local_path.write_bytes(image_data)

                # Verify it's a valid image
                from PIL import Image
                try:
                    with Image.open(local_path) as img:
                        img.verify()  # Verify integrity
                except Exception:
                    local_path.unlink(missing_ok=True)
                    raise ImageAPIError("Downloaded file is not a valid image")

                return {
                    "provider": "Pollinations-AI",
                    "seed": seed,
                    "width": width,
                    "height": height,
                    "storage_url": str(local_path),
                    "thumbnail_url": str(local_path)
                }
            else:
                error_text = resp.text
                raise ImageAPIError(f"Pollinations API error: {resp.status_code} - {error_text}")
def get_image_provider(provider_type: Optional[str] = None) -> ImageProvider:
    """
    Factory function to retrieve configured ImageProvider instance.
    Explicit provider modes:
    - 'mock': MockImageProvider
    - 'flux': FluxImageProvider (uses REPLICATE_API_KEY)
    - 'pollinations': PollinationsImageProvider (free unlimited)
    - 'auto' / None: Auto-detects key. If REPLICATE_API_KEY present, returns FluxImageProvider; else PollinationsImageProvider.
    """
    mode = (provider_type or getattr(settings, "IMAGE_PROVIDER", "auto") or os.getenv("IMAGE_PROVIDER") or "auto").lower()

    if mode == "mock":
        return MockImageProvider()

    if mode == "flux":
        return FluxImageProvider()

    if mode == "pollinations":
        return PollinationsImageProvider()

    # Auto mode
    replicate_key = getattr(settings, "REPLICATE_API_KEY", "") or os.getenv("REPLICATE_API_KEY") or os.getenv("FLUX_API_KEY") or os.getenv("IMAGE_API_KEY")
    if replicate_key:
        return FluxImageProvider(api_key=replicate_key)
    else:
        return PollinationsImageProvider()
