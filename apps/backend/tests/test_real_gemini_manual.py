"""
Manual Integration Test for Real Google Gemini LLM Provider (via AI Studio Free Tier).
This test:
- Requires an explicit GEMINI_API_KEY
- Uses LLM_PROVIDER=gemini
- Sends one tiny story generation request to the live Gemini API endpoint
- Validates the returned Story JSON schema
- Never prints secrets or API keys
- Measures and records provider, model, and request latency metadata
"""

import os
import time
import pytest
import anyio
from app.core.config import settings
from app.core.llm import OpenAILLMProvider, get_llm_provider, mask_secret
from app.services.director import DirectorAgentService
from app.services.story import StoryAgentService


pytestmark = pytest.mark.integration


@pytest.mark.anyio
async def test_real_gemini_provider_manual_execution():
    """Manual integration test against live Google Gemini API endpoint."""
    api_key = (
        os.getenv("GEMINI_API_KEY")
        or getattr(settings, "GEMINI_API_KEY", "")
    )

    if not api_key:
        pytest.skip("GEMINI_API_KEY is not configured")

    base_url = getattr(settings, "GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai") or "https://generativelanguage.googleapis.com/v1beta/openai"
    model = getattr(settings, "GEMINI_MODEL", "gemini-2.5-flash") or "gemini-2.5-flash"

    # Instantiate real Gemini provider via OpenAILLMProvider infrastructure
    provider = OpenAILLMProvider(
        api_key=api_key,
        base_url=base_url,
        model=model
    )

    # Create services using real Gemini provider
    director_service = DirectorAgentService(llm_provider=provider)
    story_service = StoryAgentService(llm_provider=provider)

    start_time = time.time()

    # 1. Generate Production Plan via Real Gemini Provider
    plan = await director_service.generate_production_plan(
        project_id="proj_manual_gemini_real",
        topic="Little Kitten Learns Primary Colors",
        target_age_group="3-5"
    )

    # 2. Generate Story Script via Real Gemini Provider
    story = await story_service.generate_story_script(production_plan=plan)

    latency = round(time.time() - start_time, 2)

    # Verify secret masking
    masked_key = mask_secret("Gemini key check", secret=api_key)
    assert api_key not in masked_key, "Secret GEMINI_API_KEY leaked in output!"

    # Verify returned Story JSON schema
    assert story is not None
    assert isinstance(story, dict)
    assert "story_title" in story
    assert "story_summary" in story
    assert "scenes" in story
    assert len(story["scenes"]) > 0

    scene1 = story["scenes"][0]
    assert "narration_text" in scene1
    assert "visual_description" in scene1

    # Record metadata without exposing secrets
    metadata = {
        "status": "SUCCESS",
        "provider": "Google Gemini (AI Studio Free Tier)",
        "provider_base_url": base_url,
        "model": model,
        "latency_seconds": latency,
        "story_title": story["story_title"],
        "scene_count": len(story["scenes"])
    }

    print("\n--- Real Gemini Provider Manual Test Metadata ---")
    for k, v in metadata.items():
        print(f"  {k}: {v}")
    print("--------------------------------------------------\n")
