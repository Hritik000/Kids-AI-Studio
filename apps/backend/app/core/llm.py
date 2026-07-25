import os
import json
import re
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

PROMPTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../../packages/prompts")
)

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
        pass

class MockLLMProvider(LLMProvider):
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

class KimiLLMProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("KIMI_API_KEY") or os.getenv("OPENAI_API_KEY")

    async def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        if not self.api_key:
            return await MockLLMProvider().generate_json(prompt, system_prompt)

        try:
            import httpx
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            body = {
                "model": "moonshot-v1-8k",
                "messages": [
                    {"role": "system", "content": system_prompt or "You are a helpful assistant that returns valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.7
            }
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post("https://api.moonshot.cn/v1/chat/completions", headers=headers, json=body)
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return json.loads(content)
        except Exception as e:
            print(f"Kimi LLM API error, falling back to mock provider: {e}")
            return await MockLLMProvider().generate_json(prompt, system_prompt)

def get_llm_provider(provider_type: str = "auto") -> LLMProvider:
    if provider_type == "mock":
        return MockLLMProvider()
    elif provider_type == "kimi":
        return KimiLLMProvider()
    else:
        if os.getenv("KIMI_API_KEY") or os.getenv("OPENAI_API_KEY"):
            return KimiLLMProvider()
        return MockLLMProvider()
