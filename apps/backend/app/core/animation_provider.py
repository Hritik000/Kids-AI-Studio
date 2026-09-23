"""
Production-Correct, Provider-Agnostic Animation Layer.
Provides clean AnimationProvider abstraction for Replicate Wan 2.1 models and Mock providers.
Features Replicate async prediction lifecycle, status polling, video container validation,
local persistent asset storage, and secret masking.
"""

import os
import time
import urllib.parse
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import httpx
from app.core.config import settings
from pathlib import Path
import hashlib
import io

logger = logging.getLogger("animation_provider")


class AnimationProviderError(Exception):
    """Base exception for all animation provider errors."""
    pass


class AnimationConfigurationError(AnimationProviderError):
    """Raised when Animation Provider configuration or API key is missing in real mode."""
    pass


class AnimationInputError(AnimationProviderError):
    """Raised when input image asset is missing or unreadable."""
    pass


class AnimationAuthError(AnimationProviderError):
    """Raised when authentication fails (HTTP 401/403)."""
    pass


class AnimationRateLimitError(AnimationProviderError):
    """Raised when rate limit is hit (HTTP 429)."""
    pass


class AnimationTimeoutError(AnimationProviderError):
    """Raised when video generation or status polling times out."""
    pass


class AnimationAPIError(AnimationProviderError):
    """Raised when generic HTTP, provider API, or video container error occurs."""
    pass


def mask_secret(text: str, secret: Optional[str] = None) -> str:
    """Masks secret API keys in log messages and error tracebacks."""
    if not text:
        return text
    secrets_to_mask = [secret] if secret else []
    for key_env in ["REPLICATE_API_KEY", "WAN_API_KEY", "ANIMATION_API_KEY"]:
        val = os.getenv(key_env) or getattr(settings, key_env, "")
        if val:
            secrets_to_mask.append(val)

    masked_text = str(text)
    for s in secrets_to_mask:
        if s and len(s) > 4:
            masked = f"{s[:3]}...{s[-4:]}"
            masked_text = masked_text.replace(s, masked)
    return masked_text


class AnimationProvider(ABC):
    @abstractmethod
    async def generate_animation_clip(
        self,
        image_url: str,
        motion_prompt: str,
        duration_seconds: float = 5.0,
        width: int = 1280,
        height: int = 720,
        seed: int = 42,
        project_id: str = "default_project"
    ) -> Dict[str, Any]:
        """Generates an animation clip and returns metadata with local persistent video storage URL."""
        pass


class MockAnimationProvider(AnimationProvider):
    """
    Deterministic Mock Animation Provider for automated unit tests and keyless local development.
    """

    async def generate_animation_clip(
        self,
        image_url: str,
        motion_prompt: str,
        duration_seconds: float = 5.0,
        width: int = 1280,
        height: int = 720,
        seed: int = 42,
        project_id: str = "default_project"
    ) -> Dict[str, Any]:
        short_prompt = motion_prompt[:40].replace(" ", "+")
        encoded = urllib.parse.quote(short_prompt)
        video_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
        thumb_url = f"https://placehold.co/400x225/1A1D27/FFFFFF/png?text=Animated+{encoded}"

        return {
            "provider": "Wan2.1-i2v-Mock",
            "seed": seed,
            "duration_seconds": duration_seconds,
            "width": width,
            "height": height,
            "storage_url": video_url,
            "thumbnail_url": image_url or thumb_url
        }


class Wan2AnimationProvider(AnimationProvider):
    """
    Production-grade Animation Provider communicating with Replicate Wan 2.1 models.
    Handles input image validation, prediction creation, bounded polling loop,
    video container inspection (FFmpeg), and local persistent video asset storage.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        poll_interval: Optional[float] = None,
        timeout_seconds: Optional[float] = None
    ):
        self.api_key = api_key or getattr(settings, "REPLICATE_API_KEY", "") or os.getenv("REPLICATE_API_KEY") or os.getenv("WAN_API_KEY") or ""
        self.model = model or getattr(settings, "ANIMATION_MODEL", "wan-video/wan-2.1-1.3b") or "wan-video/wan-2.1-1.3b"
        self.poll_interval = poll_interval or getattr(settings, "ANIMATION_POLL_INTERVAL", 2.0) or 2.0
        self.timeout_seconds = timeout_seconds or getattr(settings, "ANIMATION_TIMEOUT", 120.0) or 120.0

    async def generate_animation_clip(
        self,
        image_url: str,
        motion_prompt: str,
        duration_seconds: float = 5.0,
        width: int = 1280,
        height: int = 720,
        seed: int = 42,
        project_id: str = "default_project"
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise AnimationConfigurationError(
                "Replicate API key is missing. Set REPLICATE_API_KEY or set ANIMATION_PROVIDER=mock for development/testing."
            )

        # 1. Input Image Asset Validation
        if not image_url or not isinstance(image_url, str):
            raise AnimationInputError("Source image URL/path is empty or invalid.")

        if not (image_url.startswith("http://") or image_url.startswith("https://")):
            if not os.path.isfile(image_url):
                raise AnimationInputError(f"Source image file does not exist on disk at '{image_url}'")

        # 2. Build Replicate Prediction Creation Endpoint
        if "/" in self.model:
            create_url = f"https://api.replicate.com/v1/models/{self.model}/predictions"
            body: Dict[str, Any] = {
                "input": {
                    "image": image_url,
                    "prompt": motion_prompt,
                    "duration": duration_seconds
                }
            }
        else:
            create_url = "https://api.replicate.com/v1/predictions"
            body = {
                "version": self.model,
                "input": {
                    "image": image_url,
                    "prompt": motion_prompt,
                    "duration": duration_seconds
                }
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Prefer": "wait"
        }

        logger.info("Submitting Replicate animation video prediction request for model %s...", self.model)

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            # Create Prediction Request
            try:
                resp = await client.post(create_url, headers=headers, json=body)
            except (httpx.TimeoutException, asyncio.TimeoutError) as e:
                raise AnimationTimeoutError(f"Replicate API initial POST request timed out after {self.timeout_seconds}s") from e
            except Exception as e:
                raise AnimationAPIError(f"Failed to submit Replicate animation prediction: {mask_secret(str(e), self.api_key)}") from e

            if resp.status_code in (401, 403):
                err_text = mask_secret(resp.text, self.api_key)
                raise AnimationAuthError(f"Replicate API Authentication failed (HTTP {resp.status_code}): {err_text}")

            if resp.status_code == 429:
                err_text = mask_secret(resp.text, self.api_key)
                raise AnimationRateLimitError(f"Replicate API Rate Limit exceeded (HTTP 429): {err_text}")

            if resp.status_code >= 500:
                err_text = mask_secret(resp.text, self.api_key)
                raise AnimationAPIError(f"Replicate Server Error (HTTP {resp.status_code}): {err_text}")

            if resp.status_code >= 400:
                err_text = mask_secret(resp.text, self.api_key)
                raise AnimationAPIError(f"Replicate API Request Error (HTTP {resp.status_code}): {err_text}")

            data = resp.json()
            prediction_id = data.get("id")
            status = data.get("status")
            poll_url = data.get("urls", {}).get("get") or f"https://api.replicate.com/v1/predictions/{prediction_id}"

            # 3. Bounded Polling Loop if status is starting or processing
            if status in ("starting", "processing"):
                logger.info("Video Prediction %s status: %s. Starting polling loop (interval: %.1fs, timeout: %.1fs)...", prediction_id, status, self.poll_interval, self.timeout_seconds)
                start_poll = time.time()

                while time.time() - start_poll < self.timeout_seconds:
                    await asyncio.sleep(self.poll_interval)
                    try:
                        poll_resp = await client.get(poll_url, headers=headers)
                    except Exception as e:
                        logger.warning("Polling error for prediction %s: %s", prediction_id, mask_secret(str(e), self.api_key))
                        continue

                    if poll_resp.status_code == 429:
                        logger.warning("Rate limited during status polling (HTTP 429). Waiting 3s...")
                        await asyncio.sleep(3.0)
                        continue

                    if poll_resp.status_code >= 400:
                        err_text = mask_secret(poll_resp.text, self.api_key)
                        raise AnimationAPIError(f"Error polling video prediction status (HTTP {poll_resp.status_code}): {err_text}")

                    poll_data = poll_resp.json()
                    status = poll_data.get("status")

                    if status == "succeeded":
                        data = poll_data
                        logger.info("Video Prediction %s succeeded!", prediction_id)
                        break
                    elif status == "failed":
                        err_msg = poll_data.get("error") or "Unknown video prediction failure error"
                        raise AnimationAPIError(f"Replicate video generation failed for prediction {prediction_id}: {err_msg}")
                    elif status == "canceled":
                        raise AnimationAPIError(f"Replicate video generation was canceled for prediction {prediction_id}.")
                else:
                    raise AnimationTimeoutError(f"Replicate video generation timed out after {self.timeout_seconds}s for prediction {prediction_id}")

            if status == "failed":
                err_msg = data.get("error") or "Unknown error"
                raise AnimationAPIError(f"Replicate video generation failed: {err_msg}")

            if status == "canceled":
                raise AnimationAPIError("Replicate video generation was canceled.")

            if status != "succeeded":
                raise AnimationAPIError(f"Unexpected Replicate prediction status: {status}")

            # 4. Extract Output Video URL
            output = data.get("output")
            if isinstance(output, list) and len(output) > 0:
                raw_video_url = output[0]
            elif isinstance(output, str):
                raw_video_url = output
            else:
                raise AnimationAPIError(f"Replicate prediction {prediction_id} missing valid output video URL.")

            if not raw_video_url or not isinstance(raw_video_url, str) or not raw_video_url.startswith("http"):
                raise AnimationAPIError(f"Invalid video output URL returned by Replicate: {raw_video_url}")

            # 5. Download and Persist Video Asset locally using MediaDownloader
            from app.services.rendering.downloader import MediaDownloader
            try:
                local_asset_path = MediaDownloader.download_asset(raw_video_url, project_id=project_id)
            except Exception as e:
                raise AnimationAPIError(f"Failed to download and persist generated video from {raw_video_url}: {str(e)}") from e

            # Validate Downloaded Video File
            if not os.path.isfile(local_asset_path):
                raise AnimationAPIError(f"Downloaded video file does not exist at '{local_asset_path}'")

            file_size = os.path.getsize(local_asset_path)
            if file_size == 0:
                raise AnimationAPIError(f"Downloaded video file is empty (0 bytes) at '{local_asset_path}'")

            ext = os.path.splitext(local_asset_path)[1].lower()
            if ext not in (".mp4", ".webm", ".mov", ".mkv"):
                raise AnimationAPIError(f"Downloaded asset has non-video extension '{ext}' at '{local_asset_path}'")

            # 6. Verify container integrity via FFmpeg
            from app.services.rendering.ffmpeg import FFmpegEngine
            try:
                ret_code, stdout, stderr = FFmpegEngine.run_command(["-i", local_asset_path], timeout=15)
            except Exception as e:
                stderr = getattr(e, "stderr", str(e))

            probe_info = stderr or ""
            if "Error opening input" in probe_info or "Invalid data found" in probe_info:
                raise AnimationAPIError(f"Downloaded video asset is unreadable or corrupted at '{local_asset_path}': {probe_info}")

            logger.info("Successfully generated and persisted real video asset: %s (%d bytes)", local_asset_path, file_size)

            return {
                "provider": f"Wan2-Replicate ({self.model})",
                "seed": seed,
                "duration_seconds": duration_seconds,
                "width": width,
                "height": height,
                "storage_url": local_asset_path,
                "thumbnail_url": image_url
            }


class LocalSVDProvider(AnimationProvider):
    """Local Stable Video Diffusion optimized for Apple Silicon M4"""

    def __init__(self):
        super().__init__()
        self.pipe = None
        self.device = None
        self._is_loading = False
        self._torch_available = False
        try:
            import torch
            self.torch = torch
            self._torch_available = True
        except ImportError:
            pass

    async def _ensure_pipe_loaded(self):
        """Lazy-load the SVD pipeline to avoid blocking startup"""
        if self.pipe is None and not self._is_loading:
            self._is_loading = True
            try:
                # Import torch here to handle case where it's not available
                import torch
                from diffusers import StableVideoDiffusionPipeline

                # Set device if not already set
                if self.device is None:
                    self.device = "mps" if torch.backends.mps.is_available() else "cpu"

                logger.info("🔄 Loading Stable Video Diffusion pipeline (first run may take 2-5 minutes)...")

                # Use the img2vid variant (image-to-video)
                self.pipe = StableVideoDiffusionPipeline.from_pretrained(
                    "stabilityai/stable-video-diffusion-img2vid-1v1",
                    torch_dtype=torch.float16,
                    variant="fp16",
                )

                # Move to MPS (Apple Silicon GPU) and enable memory optimizations
                self.pipe.to(self.device)

                # Critical optimizations for M4/16GB
                self.pipe.enable_attention_slicing()
                self.pipe.enable_vae_slicing()

                # Optional: Enable xformers if installed (saves ~20% memory)
                try:
                    self.pipe.enable_xformers_memory_efficient_attention()
                    logger.info("✓ Xformers memory optimization enabled")
                except Exception:
                    logger.info("ℹ️  Xformers not available - using standard attention")

                logger.info(f"✓ SVD Pipeline loaded successfully on {self.device}")

            except Exception as e:
                raise AnimationAPIError(f"Failed to load SVD model: {str(e)}")
            finally:
                self._is_loading = False

    async def generate_animation_clip(
        self,
        image_url: str,
        motion_prompt: str,
        duration_seconds: float = 5.0,
        width: int = 1280,
        height: int = 720,
        seed: int = 42,
        project_id: str = "default_project"
    ) -> Dict[str, Any]:
        await self._ensure_pipe_loaded()

        from PIL import Image
        import numpy as np
        import imageio
        # Import torch here to handle case where it's not available
        import torch

        # Validate and prepare input image
        if not image_url or not isinstance(image_url, str):
            raise AnimationInputError("Source image URL/path is empty or invalid.")

        # Load image from URL or local path
        if image_url.startswith("http://") or image_url.startswith("https://"):
            # Download image from URL
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(image_url)
                if resp.status_code != 200:
                    raise AnimationAPIError(f"Failed to download image from {image_url}: HTTP {resp.status_code}")
                image_data = resp.content
                image = Image.open(io.BytesIO(image_data)).convert("RGB")
        else:
            # Load image from local path
            if not os.path.isfile(image_url):
                raise AnimationInputError(f"Source image file does not exist on disk at '{image_url}'")
            image = Image.open(image_url).convert("RGB")

        # Optimize for M4/16GB: use 512x512 (good balance of quality/speed)
        target_size = (512, 512)
        image = image.resize(target_size, Image.Resampling.LANCZOS)

        # Calculate frames needed (SVD generates 14 frames @ ~7fps = 2 seconds)
        # We'll loop to reach desired duration
        target_frames = int(duration_seconds * 7)  # Aim for ~7 fps
        target_frames = max(14, min(target_frames, 56))  # Clamp between 2-8 seconds worth
        loops_needed = max(1, (target_frames + 13) // 14)  # How many 14-frame chunks we need

        all_frames = []

        for loop in range(loops_needed):
            # Vary seed slightly for variation between loops
            current_seed = 42 + loop

            with torch.no_grad():
                with torch.autocast(self.device):
                    # Generate 14 frames
                    frames = self.pipe(
                        image,
                        decode_chunk_size=8,  # Good balance for memory/speed
                        motion_bucket_id=120,  # Medium motion (adjustable)
                        noise_aug_strength=0.02,
                        num_inference_steps=25,  # Balance quality/speed
                        height=target_size[1],
                        width=target_size[0],
                        seed=current_seed,
                    ).frames[0]

                    all_frames.extend(frames)

                    # Free GPU memory between iterations
                    if self.device == "mps":
                        torch.mps.empty_cache()

        # Trim to exact target duration
        all_frames = all_frames[:target_frames]

        # Prepare output path
        assets_dir = Path("/tmp/kidsai_renders") / project_id / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)

        # Generate deterministic filename
        hash_input = f"{image_url}{motion_prompt}{duration_seconds}{width}{height}"
        file_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
        local_path = assets_dir / f"asset_{file_hash}.mp4"
        thumbnail_path = assets_dir / f"asset_{file_hash}_thumb.jpg"

        # Save as MP4 using FFmpeg-compatible settings
        try:
            # Save frames as temporary PNG sequence
            temp_dir = assets_dir / f"temp_{file_hash}"
            temp_dir.mkdir(exist_ok=True)

            for i, frame in enumerate(all_frames):
                frame.save(temp_dir / f"frame_{i:04d}.png")

            # Use FFmpeg to encode video (hardware accelerated on M4)
            import subprocess
            ffmpeg_cmd = [
                'ffmpeg',
                '-y',  # Overwrite output
                '-framerate', '7',
                '-i', str(temp_dir / 'frame_%04d.png'),
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-crf', '23',  # Good quality
                '-preset', 'medium',
                str(local_path)
            ]

            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise AnimationAPIError(f"FFmpeg encoding failed: {result.stderr}")

            # Generate thumbnail from middle frame
            middle_frame = all_frames[len(all_frames)//2]
            middle_frame.save(thumbnail_path, "JPEG")

            # Cleanup
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

        except Exception as e:
            # Cleanup on error
            if 'temp_dir' in locals():
                shutil.rmtree(temp_dir, ignore_errors=True)
            raise AnimationAPIError(f"Animation processing failed: {str(e)}")

        return {
            "provider": "LocalSVD-M4",
            "seed": seed,
            "duration_seconds": duration_seconds,
            "width": width,
            "height": height,
            "storage_url": str(local_path),
            "thumbnail_url": str(thumbnail_path)
        }


def get_animation_provider(provider_type: Optional[str] = None) -> AnimationProvider:
    """
    Factory function to retrieve configured AnimationProvider instance.
    Explicit provider modes:
    - 'mock': MockAnimationProvider
    - 'wan' / 'wan2': Wan2AnimationProvider (uses REPLICATE_API_KEY)
    - 'local_svd': LocalSVDProvider (zero cost, local)
    - 'auto' / None: Auto-detects key. If REPLICATE_API_KEY present, returns Wan2AnimationProvider; else LocalSVDProvider.
    """
    mode = (provider_type or getattr(settings, "ANIMATION_PROVIDER", "auto") or os.getenv("ANIMATION_PROVIDER") or "auto").lower()

    if mode == "mock":
        return MockAnimationProvider()

    if mode in ("wan", "wan2"):
        return Wan2AnimationProvider()

    if mode == "local_svd":
        return LocalSVDProvider()

    # Auto mode
    replicate_key = getattr(settings, "REPLICATE_API_KEY", "") or os.getenv("REPLICATE_API_KEY") or os.getenv("WAN_API_KEY")
    if replicate_key:
        return Wan2AnimationProvider(api_key=replicate_key)
    else:
        return LocalSVDProvider()
