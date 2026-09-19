"""
Production-Correct, Provider-Agnostic LLM Layer.
Provides clean LLMProvider abstraction for OpenAI, Kimi Moonshot, and Mock providers.
Features robust JSON recovery, transient error retries, and secret masking.
"""

import os
import json
import re
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import httpx
from app.core.config import settings

logger = logging.getLogger("llm_provider")

PROMPTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../../packages/prompts")
)


class LLMError(Exception):
    """Base exception for all LLM errors."""
    pass


class LLMConfigurationError(LLMError):
    """Raised when LLM configuration or API key is missing in real mode."""
    pass


class LLMAuthError(LLMError):
    """Raised when authentication fails (HTTP 401/403)."""
    pass


class LLMRateLimitError(LLMError):
    """Raised when rate limit is hit (HTTP 429)."""
    pass


class LLMTimeoutError(LLMError):
    """Raised when LLM request times out."""
    pass


class LLMAPIError(LLMError):
    """Raised when generic HTTP or provider API error occurs."""
    pass


class LLMJSONParseError(LLMError):
    """Raised when LLM response text cannot be parsed as JSON."""
    pass


def mask_secret(text: str, secret: Optional[str] = None) -> str:
    """Masks secret API keys in log messages and error tracebacks."""
    if not text:
        return text
    secrets_to_mask = [secret] if secret else []
    for key_env in ["GEMINI_API_KEY", "OPENAI_API_KEY", "KIMI_API_KEY", "STORY_API_KEY"]:
        val = os.getenv(key_env) or getattr(settings, key_env, "")
        if val:
            secrets_to_mask.append(val)

    masked_text = str(text)
    for s in secrets_to_mask:
        if s and len(s) > 4:
            masked = f"{s[:3]}...{s[-4:]}"
            masked_text = masked_text.replace(s, masked)
    return masked_text


def extract_json_payload(raw_text: str) -> Dict[str, Any]:
    """
    Extracts and parses JSON object from LLM response text.
    Handles markdown code fences (```json ... ```) and surrounding commentary.
    Also handles truncated JSON by attempting to close open structures.
    """
    if not raw_text or not raw_text.strip():
        raise LLMJSONParseError("LLM response content is empty.")

    cleaned = raw_text.strip()

    # Strip markdown code blocks if present
    if "```" in cleaned:
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
        if fence_match:
            cleaned = fence_match.group(1).strip()

    # Try direct parse
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        # If direct parse fails, continue to try extraction methods
        pass

    # Remove any potential BOM or special characters that might interfere
    cleaned = cleaned.encode('utf-8', 'ignore').decode('utf-8')

    # Extract block between first { and last }
    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")

    # If we have both braces, try the standard extraction
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        json_candidate = cleaned[first_brace:last_brace + 1]
        try:
            data = json.loads(json_candidate)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError as e:
            # If standard extraction fails, log and continue to try fixes
            pass

    # If we have an opening brace but no closing brace, try to add one
    if first_brace != -1 and last_brace == -1:
        # Try to extract from the first brace to the end and see if we can make it valid
        json_candidate = cleaned[first_brace:]

        # Try to parse as-is first
        try:
            data = json.loads(json_candidate)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass

        # If that fails, try adding a closing brace
        json_candidate_with_close = json_candidate + "}"
        try:
            data = json.loads(json_candidate_with_close)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass

    # Last resort: try to find any valid JSON object by scanning from the start
    # Look for the longest valid JSON substring starting from the first brace
    if first_brace != -1:
        # Try progressively shorter substrings from the end
        for i in range(len(cleaned), first_brace, -1):
            json_candidate = cleaned[first_brace:i]
            # Try as-is
            try:
                data = json.loads(json_candidate)
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                # Try removing trailing comma if present
                if json_candidate.endswith(','):
                    json_candidate_no_comma = json_candidate[:-1]
                    try:
                        data = json.loads(json_candidate_no_comma)
                        if isinstance(data, dict):
                            return data
                    except json.JSONDecodeError:
                        pass
                continue

        # Try progressively longer substrings from the start (adding closing braces)
        for i in range(first_brace + 1, len(cleaned) + 1):
            json_candidate = cleaned[first_brace:i]
            # Try as-is
            try:
                data = json.loads(json_candidate)
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                # Try removing trailing comma if present
                if json_candidate.endswith(','):
                    json_candidate_no_comma = json_candidate[:-1]
                    try:
                        data = json.loads(json_candidate_no_comma)
                        if isinstance(data, dict):
                            return data
                    except json.JSONDecodeError:
                        pass
                # Try with closing braces (try 1 to 3 closing braces)
                for num_braces in range(1, 4):
                    try:
                        data = json.loads(json_candidate + "}" * num_braces)
                        if isinstance(data, dict):
                            return data
                    except json.JSONDecodeError:
                        # Try removing trailing comma if present
                        if (json_candidate + "}" * num_braces).endswith(','):
                            json_candidate_no_comma = json_candidate + "}" * (num_braces - 1)
                            try:
                                data = json.loads(json_candidate_no_comma)
                                if isinstance(data, dict):
                                    return data
                            except json.JSONDecodeError:
                                continue

    raise LLMJSONParseError(f"No valid JSON object found in response: {cleaned[:100]}...")


class PromptLoader:
    @staticmethod
    def load_prompt(filename: str, variables: Optional[Dict[str, Any]] = None) -> str:
        filepath = os.path.join(PROMPTS_DIR, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Prompt file not found at {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        if variables:
            for key, val in variables.items():
                placeholder = f"{{{{{key}}}}}"
                content = content.replace(placeholder, str(val))

        return content


class LLMProvider(ABC):
    @abstractmethod
    async def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Generates structured JSON from the LLM provider."""
        pass

    @abstractmethod
    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generates raw text from the LLM provider."""
        pass


class OpenAILLMProvider(LLMProvider):
    """
    Production-grade LLM provider supporting OpenAI-compatible REST APIs
    (OpenAI, Moonshot Kimi, DeepSeek, Azure, etc.).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        max_retries: int = 3,
        timeout_seconds: float = 60.0
    ):
        self.api_key = api_key or getattr(settings, "OPENAI_API_KEY", "") or os.getenv("OPENAI_API_KEY") or os.getenv("STORY_API_KEY") or ""
        self.model = model or getattr(settings, "OPENAI_MODEL", "gpt-4o-mini") or "gpt-4o-mini"
        raw_base_url = base_url or getattr(settings, "OPENAI_BASE_URL", "https://api.openai.com/v1") or "https://api.openai.com/v1"
        self.base_url = raw_base_url.rstrip("/")
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds

    async def _call_completion_api(self, prompt: str, system_prompt: Optional[str] = None, json_mode: bool = True) -> str:
        if not self.api_key:
            raise LLMConfigurationError(
                "LLM API key is missing. Set OPENAI_API_KEY or set LLM_PROVIDER=mock for development/testing."
            )

        endpoint = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        body: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7
        }
        if json_mode:
            body["response_format"] = {"type": "json_object"}

        last_exception: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(
                    "Executing LLM request (Attempt %d/%d) to model %s via %s",
                    attempt, self.max_retries, self.model, self.base_url
                )
                async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                    resp = await client.post(endpoint, headers=headers, json=body)

                    if resp.status_code in (401, 403):
                        err_text = mask_secret(resp.text, self.api_key)
                        raise LLMAuthError(f"LLM Authentication failed (HTTP {resp.status_code}): {err_text}")

                    if resp.status_code == 429:
                        err_text = mask_secret(resp.text, self.api_key)
                        raise LLMRateLimitError(f"LLM Rate limit exceeded (HTTP 429): {err_text}")

                    if resp.status_code >= 500:
                        err_text = mask_secret(resp.text, self.api_key)
                        raise LLMAPIError(f"LLM Server Error (HTTP {resp.status_code}): {err_text}")

                    resp.raise_for_status()
                    data = resp.json()

                    if "choices" not in data or not data["choices"]:
                        raise LLMAPIError("LLM response missing 'choices' field.")

                    content = data["choices"][0]["message"]["content"]
                    return content

            except (LLMAuthError, LLMConfigurationError):
                # Deterministic auth/config errors should NOT be retried
                raise

            except LLMRateLimitError as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = 1.0 * (2 ** (attempt - 1))
                    logger.warning("Rate limited (HTTP 429). Retrying in %.1fs...", delay)
                    await asyncio.sleep(delay)

            except LLMAPIError as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = 1.0 * (2 ** (attempt - 1))
                    logger.warning("LLM API Error: %s. Retrying in %.1fs...", mask_secret(str(e), self.api_key), delay)
                    await asyncio.sleep(delay)

            except (httpx.TimeoutException, asyncio.TimeoutError) as e:
                last_exception = LLMTimeoutError(f"LLM request timed out after {self.timeout_seconds}s")
                if attempt < self.max_retries:
                    delay = 1.0 * (2 ** (attempt - 1))
                    logger.warning("LLM request timed out. Retrying in %.1fs...", delay)
                    await asyncio.sleep(delay)

            except Exception as e:
                masked_err = mask_secret(str(e), self.api_key)
                last_exception = LLMAPIError(f"LLM request failed: {masked_err}")
                if attempt < self.max_retries:
                    delay = 1.0 * (2 ** (attempt - 1))
                    await asyncio.sleep(delay)

        raise last_exception or LLMAPIError("LLM request failed after retries.")

    async def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        content = await self._call_completion_api(prompt, system_prompt=system_prompt, json_mode=True)
        return extract_json_payload(content)

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return await self._call_completion_api(prompt, system_prompt=system_prompt, json_mode=False)


class MockLLMProvider(LLMProvider):
    """
    Deterministic Mock LLM Provider for automated unit tests and keyless local development.
    """

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return "Mock LLM text output for prompt."

    async def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        # 1. Director Agent Production Plan Mock
        if "Director Agent Master Protocol" in prompt or "production_plan" in prompt.lower() or "Educational Objective" in prompt:
            topic_match = re.search(r"Topic:\s*(.*)", prompt)
            topic = topic_match.group(1).strip() if topic_match else "Dinosaurs Learn Colors"

            age_match = re.search(r"Target Age Group:\s*(.*)", prompt)
            age_group = age_match.group(1).strip() if age_match else "3-5"

            style_match = re.search(r"Visual Style:\s*(.*)", prompt)
            style = style_match.group(1).strip() if style_match else "3D Pixar Render"

            return {
                "project_id": "proj_mock_plan",
                "topic": topic,
                "educational_objective": f"Teach children about core educational concepts in a fun story about {topic}",
                "target_age_group": age_group,
                "estimated_duration_seconds": 60.0,
                "scene_count": 4,
                "narration_style": "Enthusiastic, warm, and gentle storyteller",
                "visual_style": style,
                "character_requirements": [
                    {
                        "name": "Rexy",
                        "description": "Friendly green baby T-Rex with big curious eyes and a cheerful smile",
                        "role": "Protagonist"
                    },
                    {
                        "name": "Penny",
                        "description": "Bright yellow Pterodactyl wearing a tiny blue explorer cap",
                        "role": "Guide & Friend"
                    }
                ],
                "music_mood_plan": "Upbeat acoustic guitar, joyful marimba, and soft playful woodwinds",
                "animation_style_plan": "Vibrant 3D character motion with gentle pan-and-zoom camera framing",
                "thumbnail_concept_plan": "Rexy holding a glowing colorful star in a lush 3D dinosaur valley",
                "seo_strategy_plan": {
                    "target_keywords": [topic.lower(), "learning for kids", "toddler education", "nursery cartoon"],
                    "category": "Education"
                },
                "quality_rules": [
                    "Strictly child-safe content with zero scary elements",
                    "Clear audio-visual synchronization",
                    "High color vibrancy and positive moral lesson"
                ],
                "retry_strategy": {
                    "max_retries": 3,
                    "fallback_provider": "mock-llm-v1"
                }
            }

        # 2. Storyboard Agent Master Prompt Mock
        elif "Storyboard Agent Master Prompt" in prompt or "global_color_palette" in prompt:
            return {
                "project_id": "proj_mock_sb",
                "story_title": "Rexy's Colorful Rainbow Party",
                "total_scenes": 4,
                "total_duration_seconds": 60.0,
                "visual_style": "3D Pixar Render",
                "global_color_palette": ["Lime Green", "Bright Yellow", "Sky Blue", "Sunny Orange"],
                "scenes": [
                    {
                        "scene_number": 1,
                        "scene_title": "Morning in the Dino Valley",
                        "purpose": "Establish hero character and peaceful valley environment",
                        "learning_goal": "Identify morning routine & peaceful setting",
                        "estimated_duration": 15.0,
                        "energy_level": "Medium",
                        "scene_importance": "High",
                        "narrative_arc": {
                            "beginning": "Rexy wakes up in the lush green meadow",
                            "middle": "Rexy stretches his arms happily at the golden morning sun",
                            "ending": "Penny the Pterodactyl flies down to greet Rexy"
                        },
                        "narration_text": "High up in the sunny green valley, Rexy the baby dinosaur woke up ready for a colorful adventure!",
                        "visual_plan": {
                            "environment": "Sunny Dinosaur Meadow",
                            "time_of_day": "Morning Golden Hour",
                            "weather": "Clear & Sunny",
                            "background": "Rolling emerald hills, gentle distant volcanoes, giant colorful sunflowers",
                            "foreground": "Soft grass with sparkling dew drops",
                            "key_objects": ["Giant Sunflower", "Sparkling Dew"],
                            "color_palette": ["Lime Green", "Golden Yellow", "Sky Blue"],
                            "lighting_style": "Soft Warm Golden Sunlight",
                            "mood": "Cheerful & Inviting",
                            "atmosphere": "Magical & Serene",
                            "composition": "Rule of thirds centering Rexy on grass"
                        },
                        "camera_plan": {
                            "shot_type": "Wide Shot",
                            "angle": "Eye Level",
                            "movement": "Slow Pan",
                            "camera_direction": "Left to Right",
                            "camera_speed": "Gentle",
                            "focal_point": "Rexy the baby T-Rex"
                        },
                        "transition": {
                            "type": "Cross Fade",
                            "duration_seconds": 1.0
                        },
                        "character_references": [
                            {
                                "character_name": "Rexy",
                                "expression": "Joyful & Energetic",
                                "pose": "Stretching with arms wide open",
                                "eye_direction": "Towards camera / viewer",
                                "interaction": "Greeting the morning sun",
                                "visibility": "Full Body",
                                "importance": "Primary Hero"
                            }
                        ]
                    },
                    {
                        "scene_number": 2,
                        "scene_title": "Discovering Red Strawberries",
                        "purpose": "Introduce color RED with strawberry bush discovery",
                        "learning_goal": "Identify color RED",
                        "estimated_duration": 15.0,
                        "energy_level": "High",
                        "scene_importance": "High",
                        "narrative_arc": {
                            "beginning": "Penny swoops over to a glowing strawberry bush",
                            "middle": "Rexy walks over and inspects a shiny red strawberry",
                            "ending": "Rexy smiles broadly pointing to the color Red"
                        },
                        "narration_text": "Look! Penny found a bush of juicy RED strawberries! Red is bright and sweet!",
                        "visual_plan": {
                            "environment": "Strawberry Bush Glade",
                            "time_of_day": "Bright Mid-Morning",
                            "weather": "Sunny",
                            "background": "Thick fern leaves, tall palm trees",
                            "foreground": "Glossy red strawberries hanging on green vines",
                            "key_objects": ["Red Strawberries", "Fern Leaves"],
                            "color_palette": ["Glossy Red", "Emerald Green", "Bright Yellow"],
                            "lighting_style": "Vibrant Sunlight with Soft Highlights",
                            "mood": "Excited & Curious",
                            "atmosphere": "Playful",
                            "composition": "Medium close-up on strawberry bush"
                        },
                        "camera_plan": {
                            "shot_type": "Medium Shot",
                            "angle": "Slight Low Angle",
                            "movement": "Zoom In",
                            "camera_direction": "Forward",
                            "camera_speed": "Gentle",
                            "focal_point": "Bright Red Strawberries"
                        },
                        "transition": {
                            "type": "Slide",
                            "duration_seconds": 0.8
                        },
                        "character_references": [
                            {
                                "character_name": "Rexy",
                                "expression": "Amazed & Delighted",
                                "pose": "Pointing eager finger at strawberries",
                                "eye_direction": "Towards strawberries",
                                "interaction": "Reaching towards fruit",
                                "visibility": "Three-Quarter Body",
                                "importance": "Primary Hero"
                            },
                            {
                                "character_name": "Penny",
                                "expression": "Encouraging & Proud",
                                "pose": "Hovering above bush with wings spread",
                                "eye_direction": "Towards Rexy",
                                "interaction": "Guiding Rexy to red fruit",
                                "visibility": "Full Body",
                                "importance": "Supporting Guide"
                            }
                        ]
                    },
                    {
                        "scene_number": 3,
                        "scene_title": "The Sparkling Blue River",
                        "purpose": "Introduce color BLUE by the riverbank",
                        "learning_goal": "Identify color BLUE",
                        "estimated_duration": 15.0,
                        "energy_level": "Medium",
                        "scene_importance": "High",
                        "narrative_arc": {
                            "beginning": "The friends arrive at a crystal clear river",
                            "middle": "Floating blue berries catch Rexy's eye on lily pads",
                            "ending": "Penny dips a toe in the sparkling water"
                        },
                        "narration_text": "Next to the river, they spotted BLUE berries floating like tiny blue stars!",
                        "visual_plan": {
                            "environment": "Sparkling Riverbank",
                            "time_of_day": "Noon",
                            "weather": "Clear Sky",
                            "background": "Smooth river stones, gentle waterfall in distance",
                            "foreground": "Cobblestones and floating green lily pads",
                            "key_objects": ["Blue Berries", "Lily Pads", "Water Ripples"],
                            "color_palette": ["Cobalt Blue", "Turquoise", "Lime Green"],
                            "lighting_style": "Direct Shimmering Sunlight",
                            "mood": "Peaceful & Wondrous",
                            "atmosphere": "Refreshing & Cool",
                            "composition": "Low angle tracking water line"
                        },
                        "camera_plan": {
                            "shot_type": "Low Angle",
                            "angle": "Low Angle",
                            "movement": "Tracking",
                            "camera_direction": "Along River Current",
                            "camera_speed": "Slow",
                            "focal_point": "Floating Blue Berries"
                        },
                        "transition": {
                            "type": "Cross Fade",
                            "duration_seconds": 1.0
                        },
                        "character_references": [
                            {
                                "character_name": "Rexy",
                                "expression": "Gentle Wonder",
                                "pose": "Kneeling by river edge",
                                "eye_direction": "Watching blue berries float",
                                "interaction": "Cupping water gently",
                                "visibility": "Full Body",
                                "importance": "Primary Hero"
                            }
                        ]
                    },
                    {
                        "scene_number": 4,
                        "scene_title": "Rainbow Celebration Finale",
                        "purpose": "Consolidate learning (Red + Blue + Yellow = Rainbow) and cheerful wrap-up",
                        "learning_goal": "Reinforce color recognition and goodbye gesture",
                        "estimated_duration": 15.0,
                        "energy_level": "High",
                        "scene_importance": "Hero Finale",
                        "narrative_arc": {
                            "beginning": "A vibrant rainbow stretches across the entire sky",
                            "middle": "Rexy and Penny dance together on a hilltop under rainbow",
                            "ending": "Both characters wave at the viewer as flower confetti falls"
                        },
                        "narration_text": "Together, Red and Blue make the valley sparkle! What a wonderful day of colors with Rexy and Penny!",
                        "visual_plan": {
                            "environment": "Rainbow Hilltop Overlook",
                            "time_of_day": "Late Afternoon Golden Hour",
                            "weather": "Rainbow after gentle rain",
                            "background": "Huge arc rainbow crossing blue sky, whole valley visible below",
                            "foreground": "Colorful flower petals gently floating in the air",
                            "key_objects": ["Vibrant Rainbow", "Flower Confetti"],
                            "color_palette": ["Rainbow Spectrum", "Golden Sunlight", "Lush Green"],
                            "lighting_style": "Radiant Rainbow Glow",
                            "mood": "Celebratory & Heartwarming",
                            "atmosphere": "Magical & Joyful",
                            "composition": "Wide hero shot with rainbow framing characters"
                        },
                        "camera_plan": {
                            "shot_type": "Wide Shot",
                            "angle": "Eye Level",
                            "movement": "Zoom Out",
                            "camera_direction": "Backward Pull",
                            "camera_speed": "Gentle",
                            "focal_point": "Rexy and Penny Waving"
                        },
                        "transition": {
                            "type": "Fade",
                            "duration_seconds": 1.5
                        },
                        "character_references": [
                            {
                                "character_name": "Rexy",
                                "expression": "Big Radiant Smile",
                                "pose": "Jumping joyfully with hands waving",
                                "eye_direction": "Directly at audience / camera",
                                "interaction": "Waving goodbye to viewers",
                                "visibility": "Full Body Center",
                                "importance": "Primary Hero"
                            },
                            {
                                "character_name": "Penny",
                                "expression": "Happy & Cheerful",
                                "pose": "Flying loops around Rexy waving wing",
                                "eye_direction": "Directly at audience",
                                "interaction": "Waving goodbye to viewers",
                                "visibility": "Full Body Side",
                                "importance": "Supporting Guide"
                            }
                        ]
                    }
                ]
            }

        # 3. Story Agent Mock Script Default
        else:
            return {
                "story_title": "Rexy's Colorful Rainbow Party",
                "story_summary": "Rexy the T-Rex and Penny the Pterodactyl explore a magical dinosaur valley to discover red strawberries, blue berries, and yellow suns!",
                "educational_goal": "Identify primary colors (Red, Blue, Yellow) through engaging visual discovery.",
                "ending_call_to_action": "Can you spot something red or blue near you today?",
                "characters": [
                    {
                        "name": "Rexy",
                        "species_or_type": "Baby T-Rex",
                        "visual_features": "Soft lime-green scales, oversized cheerful eyes, orange polka dots",
                        "personality": "Playful, curious, enthusiastic"
                    },
                    {
                        "name": "Penny",
                        "species_or_type": "Pterodactyl",
                        "visual_features": "Bright yellow wings, blue explorer hat, friendly beak",
                        "personality": "Smart, helpful, encouraging"
                    }
                ],
                "scenes": [
                    {
                        "scene_number": 1,
                        "narration_text": "High up in the sunny green valley, Rexy the baby dinosaur woke up ready for a colorful adventure!",
                        "visual_description": "A vibrant 3D Pixar-style sunny meadow with lush green hills and giant cheerful flowers. Rexy the baby T-Rex stretches happily.",
                        "educational_goal": "Introduce the main character and setting.",
                        "estimated_duration": 15.0,
                        "camera_direction": "Slow pan left to right, ending in a medium close-up of Rexy",
                        "emotion": "Joyful & Energetic",
                        "transition": "Cross Fade"
                    },
                    {
                        "scene_number": 2,
                        "narration_text": "Look! Penny found a bush of juicy RED strawberries! Red is bright and sweet!",
                        "visual_description": "Penny the Pterodactyl fluttered down next to a sparkling bush filled with bright glossy red strawberries. Rexy points at them excitedly.",
                        "educational_goal": "Teach the color RED.",
                        "estimated_duration": 15.0,
                        "camera_direction": "Zoom in on the bright red strawberries as Rexy reaches out",
                        "emotion": "Curious & Excited",
                        "transition": "Smooth Wipe"
                    },
                    {
                        "scene_number": 3,
                        "narration_text": "Next to the river, they spotted BLUE berries floating like tiny blue stars!",
                        "visual_description": "Rexy and Penny stand near a clear sparkling blue river. Glowing blue berries bob on lily pads under gentle sunlight.",
                        "educational_goal": "Teach the color BLUE.",
                        "educational_objective": "Color recognition",
                        "estimated_duration": 15.0,
                        "camera_direction": "Gentle low angle shot tracking the blue berries along the water",
                        "emotion": "Wonder & Delight",
                        "transition": "Cross Fade"
                    },
                    {
                        "scene_number": 4,
                        "narration_text": "Together, Red and Blue make the valley sparkle! What a wonderful day of colors with Rexy and Penny!",
                        "visual_description": "Rexy and Penny celebrate on a hill under a bright rainbow. Confetti of flowers gently falls as they wave at the viewer.",
                        "educational_goal": "Reinforce color learning and cheerful wrap-up.",
                        "estimated_duration": 15.0,
                        "camera_direction": "Wide pull-back hero shot revealing the beautiful full rainbow",
                        "emotion": "Celebratory & Warm",
                        "transition": "Fade to Black"
                    }
                ]
            }


class MLXLLMProvider(LLMProvider):
    """Local MLX-LM provider for Phi-3-mini on Apple Silicon"""

    def __init__(
        self,
        model: Optional[str] = None,
        max_retries: int = 3,
        timeout_seconds: float = 120.0
    ):
        self.model = model or getattr(settings, "LOCAL_MLX_MODEL_NAME", "phi-3-mini") or "phi-3-mini"
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        # mlx-lm handles model loading internally, we don't need to store the model/tokenizer here
        # They will be loaded on first use via mlx_lm.load()

    async def _call_mlx_api(self, prompt: str, system_prompt: Optional[str] = None, json_mode: bool = True) -> str:
        from mlx_lm import load, generate
        from mlx_lm.sample_utils import make_sampler

        # Determine if we're using Phi-3-mini instruct model (most common)
        model_name = self.model

        last_exception: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(
                    "Executing MLX-LM request (Attempt %d/%d) for model %s",
                    attempt, self.max_retries, model_name
                )

                # Load model and tokenizer (mlx-lm caches these)
                model, tokenizer = load(f"mlx-community/{model_name}-4bit")

                # Format prompt using Phi-3 chat format
                # Phi-3 uses <|system|>, <|user|>, <|assistant|> tokens
                formatted_prompt = ""
                if system_prompt:
                    formatted_prompt += f"<|system|>\n{system_prompt}\n"
                formatted_prompt += f"<|user|>\n{prompt}\n<|assistant|>\n"

                logger.debug(f"Formatted prompt being sent to model (first 200 chars): {formatted_prompt[:200]}")
                logger.debug(f"System prompt: {system_prompt[:100] if system_prompt else None}")
                logger.debug(f"User prompt: {prompt[:100]}")

                temp = 0.0 if json_mode else 0.7
                sampler = make_sampler(temp=temp)
                response = generate(
                    model,
                    tokenizer,
                    prompt=formatted_prompt,
                    max_tokens=500 if json_mode else 200,
                    sampler=sampler,
                )

                logger.debug(f"Raw response from model (first 200 chars): {response[:200]}")
                return response

            except Exception as e:
                masked_err = str(e)
                last_exception = Exception(f"MLX-LM request failed: {masked_err}")
                if attempt < self.max_retries:
                    delay = 1.0 * (2 ** (attempt - 1))
                    logger.warning("MLX-LM Error: %s. Retrying in %.1fs...", masked_err, delay)
                    await asyncio.sleep(delay)

        raise last_exception or Exception("MLX-LM request failed after retries.")

    async def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        content = await self._call_mlx_api(prompt, system_prompt=system_prompt, json_mode=True)
        logger.debug(f"Raw LLM response for JSON generation: {content}")
        return extract_json_payload(content)

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        content = await self._call_mlx_api(prompt, system_prompt=system_prompt, json_mode=False)
        logger.debug(f"Raw LLM response for text generation: {content}")
        return content


def get_llm_provider(provider_type: Optional[str] = None) -> LLMProvider:
    """
    Factory function to retrieve configured LLMProvider instance.
    Explicit provider modes:
    - 'mock': MockLLMProvider
    - 'gemini': OpenAILLMProvider configured for Google Gemini API via OpenAI-compatible endpoint
    - 'openai': OpenAILLMProvider (uses OPENAI_API_KEY)
    - 'kimi': OpenAILLMProvider configured for Moonshot Kimi API
    - 'local_mlx': MLXLLMProvider (local Phi-3-mini via MLX-LM, zero cost)
    - 'auto' / None: Auto-detects key in order: Gemini -> OpenAI -> Kimi -> Local MLX -> Mock.
    """
    mode = (provider_type or getattr(settings, "LLM_PROVIDER", "auto") or os.getenv("LLM_PROVIDER") or "auto").lower()

    if mode == "mock":
        return MockLLMProvider()

    if mode == "gemini":
        gemini_key = getattr(settings, "GEMINI_API_KEY", "") or os.getenv("GEMINI_API_KEY") or ""
        gemini_model = getattr(settings, "GEMINI_MODEL", "gemini-2.5-flash") or os.getenv("GEMINI_MODEL") or "gemini-2.5-flash"
        gemini_base = getattr(settings, "GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai") or "https://generativelanguage.googleapis.com/v1beta/openai"
        return OpenAILLMProvider(
            api_key=gemini_key,
            base_url=gemini_base,
            model=gemini_model
        )

    if mode == "openai":
        openai_key = getattr(settings, "OPENAI_API_KEY", "") or os.getenv("OPENAI_API_KEY") or os.getenv("STORY_API_KEY") or ""
        openai_model = getattr(settings, "OPENAI_MODEL", "gpt-4o-mini") or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
        openai_base = getattr(settings, "OPENAI_BASE_URL", "https://api.openai.com/v1") or "https://api.openai.com/v1"
        return OpenAILLMProvider(
            api_key=openai_key,
            base_url=openai_base,
            model=openai_model
        )

    if mode == "kimi":
        kimi_key = getattr(settings, "KIMI_API_KEY", "") or os.getenv("KIMI_API_KEY") or ""
        return OpenAILLMProvider(
            api_key=kimi_key,
            base_url="https://api.moonshot.cn/v1",
            model="moonshot-v1-8k"
        )

    if mode == "local_mlx":
        return MLXLLMProvider()

    # Auto mode: check keys in order: Gemini -> OpenAI -> Kimi -> Local MLX -> Mock
    gemini_key = getattr(settings, "GEMINI_API_KEY", "") or os.getenv("GEMINI_API_KEY")
    openai_key = getattr(settings, "OPENAI_API_KEY", "") or os.getenv("OPENAI_API_KEY") or os.getenv("STORY_API_KEY")
    kimi_key = getattr(settings, "KIMI_API_KEY", "") or os.getenv("KIMI_API_KEY")
    local_mlx_model = getattr(settings, "LOCAL_MLX_MODEL_NAME", "") or os.getenv("LOCAL_MLX_MODEL_NAME")

    if gemini_key:
        gemini_model = getattr(settings, "GEMINI_MODEL", "gemini-2.5-flash") or os.getenv("GEMINI_MODEL") or "gemini-2.5-flash"
        gemini_base = getattr(settings, "GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai") or "https://generativelanguage.googleapis.com/v1beta/openai"
        return OpenAILLMProvider(
            api_key=gemini_key,
            base_url=gemini_base,
            model=gemini_model
        )
    elif openai_key:
        openai_model = getattr(settings, "OPENAI_MODEL", "gpt-4o-mini") or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
        openai_base = getattr(settings, "OPENAI_BASE_URL", "https://api.openai.com/v1") or "https://api.openai.com/v1"
        return OpenAILLMProvider(
            api_key=openai_key,
            base_url=openai_base,
            model=openai_model
        )
    elif kimi_key:
        return OpenAILLMProvider(
            api_key=kimi_key,
            base_url="https://api.moonshot.cn/v1",
            model="moonshot-v1-8k"
        )
    elif local_mlx_model:  # If local MLX model is configured, use it
        return MLXLLMProvider()
    else:
        return MockLLMProvider()
