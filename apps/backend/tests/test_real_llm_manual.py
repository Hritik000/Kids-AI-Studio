"""
Manual Integration Test for Real LLM Provider (OpenAI / Moonshot Kimi).
This test:
- Requires an explicit API key (OPENAI_API_KEY or KIMI_API_KEY or STORY_API_KEY)
- Fails clearly with instructions when the key is missing
- Sends one tiny story generation request to the real API provider
- Validates the returned Story JSON schema
- Never prints secrets or API keys
- Measures and records provider, model, and request latency metadata
"""

import os
import time
import pytest
import anyio
from app.core.config import settings
from app.core.llm import OpenAILLMProvider, LLMConfigurationError, mask_secret
from app.services.director import DirectorAgentService
from app.services.story import StoryAgentService


@pytest.mark.anyio
async def test_real_llm_provider_manual_execution():
    """Manual integration test against live LLM API endpoint."""
    api_key = (
        os.getenv("OPENAI_API_KEY")
        or os.getenv("KIMI_API_KEY")
        or os.getenv("STORY_API_KEY")
        or getattr(settings, "OPENAI_API_KEY", "")
        or getattr(settings, "KIMI_API_KEY", "")
    )

    if not api_key:
        pytest.fail(
            "MANUAL TEST SKIPPED / FAILED: Real LLM API key missing.\n"
            "To run this manual integration test, supply a real API key:\n"
            "  OPENAI_API_KEY=sk-... PYTHONPATH=. ./.venv/bin/pytest tests/test_real_llm_manual.py\n"
            "or set KIMI_API_KEY=..."
        )

    base_url = (
        "https://api.moonshot.cn/v1" if os.getenv("KIMI_API_KEY") or getattr(settings, "KIMI_API_KEY", "")
        else getattr(settings, "OPENAI_BASE_URL", "https://api.openai.com/v1")
    )
    model = (
        "moonshot-v1-8k" if "moonshot" in base_url
        else getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")
    )

    # Instantiate real provider
    provider = OpenAILLMProvider(api_key=api_key, base_url=base_url, model=model)

    # Create services using real provider
    director_service = DirectorAgentService(llm_provider=provider)
    story_service = StoryAgentService(llm_provider=provider)

    start_time = time.time()

    # 1. Generate Production Plan via Real Provider
    plan = await director_service.generate_production_plan(
        project_id="proj_manual_real_llm",
        topic="Baby Panda Learns Counting 1 to 3",
        target_age_group="3-5"
    )

    # 2. Generate Story Script via Real Provider
    story = await story_service.generate_story_script(production_plan=plan)

    latency = round(time.time() - start_time, 2)

    # Verify secret masking
    masked_key = mask_secret("Key check", secret=api_key)
    assert api_key not in masked_key, "Secret API key leaked in output!"

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
        "provider_base_url": base_url,
        "model": model,
        "latency_seconds": latency,
        "story_title": story["story_title"],
        "scene_count": len(story["scenes"])
    }

    print("\n--- Real LLM Provider Manual Test Metadata ---")
    for k, v in metadata.items():
        print(f"  {k}: {v}")
    print("----------------------------------------------\n")
