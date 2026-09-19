import os
import secrets
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Dict, Any


def get_settings() -> BaseSettings:
    """Factory function to create settings with correct env file."""
    # Determine environment
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    # Determine which env file to load
    if env in ["development", "staging", "production"]:
        env_file = f".env.{env}"
    else:
        env_file = ".env"
    
    # Create settings class with the correct env file
    class EnvSettings(BaseSettings):
        PROJECT_NAME: str = "KidsAI Studio API"
        VERSION: str = "0.1.0"
        API_V1_STR: str = "/api/v1"
        
        # Environment
        ENVIRONMENT: str = env
        
        # Supabase
        SUPABASE_URL: str = ""
        SUPABASE_SERVICE_ROLE_KEY: str = ""
        SUPABASE_ANON_KEY: str = ""
        
        # AI API Keys & Endpoints (Configurable via env)
        STORY_API_KEY: str = ""
        IMAGE_API_KEY: str = ""
        TTS_API_KEY: str = ""

        # LLM Settings
        LLM_PROVIDER: str = "auto"  # auto | gemini | openai | kimi | local_mlx | mock
        GEMINI_API_KEY: str = ""
        GEMINI_MODEL: str = "gemini-2.5-flash"
        GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/openai"
        OPENAI_API_KEY: str = ""
        OPENAI_MODEL: str = "gpt-4o-mini"
        OPENAI_BASE_URL: str = "https://api.openai.com/v1"
        KIMI_API_KEY: str = ""
        LOCAL_MLX_MODEL_NAME: str = "phi-3-mini"  # Only used when LLM_PROVIDER=local_mlx

        # Image Provider Settings
        IMAGE_PROVIDER: str = "auto"  # auto | flux | pollinations | mock
        REPLICATE_API_KEY: str = ""
        IMAGE_MODEL: str = "black-forest-labs/flux-schnell"
        IMAGE_POLL_INTERVAL: float = 1.0
        IMAGE_TIMEOUT: float = 60.0

        # Animation Provider Settings
        ANIMATION_PROVIDER: str = "auto"  # auto | wan | local_svd | mock
        ANIMATION_MODEL: str = "wan-video/wan-2.1-1.3b"
        ANIMATION_POLL_INTERVAL: float = 2.0
        ANIMATION_TIMEOUT: float = 120.0

        # Voice / TTS Provider Settings
        VOICE_PROVIDER: str = "auto"  # auto | elevenlabs | kokoro | mock
        ELEVENLABS_API_KEY: str = ""
        ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"
        ELEVENLABS_MODEL: str = "eleven_multilingual_v2"
        VOICE_TIMEOUT: float = 35.0

        # Music / Audio Provider Settings
        MUSIC_PROVIDER: str = "auto"  # auto | stable_audio | huggingface_musicgen | mock
        STABLE_AUDIO_API_KEY: str = ""
        STABILITY_API_KEY: str = ""
        MUSIC_MODEL: str = "stable-audio"
        MUSIC_POLL_INTERVAL: float = 2.0
        MUSIC_TIMEOUT: float = 60.0
        HF_API_TOKEN: str = ""  # For Hugging Face Inference API
        
        # Storage & Rendering
        R2_BUCKET_URL: str = ""
        FFMPEG_PATH: str = ""
        
        # Security
        SECRET_KEY: str = ""
        ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
        REFRESH_TOKEN_EXPIRE_DAYS: int = 7

        model_config = SettingsConfigDict(
            env_file=env_file,
            env_file_encoding='utf-8',
            case_sensitive=False,
            extra="ignore"
        )

        def validate_required_settings(self):
            """Validate that all required settings are present in non-mock mode."""
            # Skip validation in development with mock providers enabled
            if self.ENVIRONMENT == "development" and self.LLM_PROVIDER == "mock":
                return
            
            # For production, validate critical settings
            if self.ENVIRONMENT == "production":
                required_in_production = [
                    "SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY",
                    "SECRET_KEY"
                ]
                
                # At least one LLM provider
                has_llm_key = bool(
                    self.GEMINI_API_KEY or 
                    self.OPENAI_API_KEY or 
                    self.KIMI_API_KEY
                )
                
                # At least one media provider set (we'll check these later in services)
                has_media_config = bool(
                    self.REPLICATE_API_KEY or 
                    self.ELEVENLABS_API_KEY or 
                    self.STABLE_AUDIO_API_KEY or
                    self.STABILITY_API_KEY or
                    self.HF_API_TOKEN  # Hugging Face token for music
                )
                
                missing = [key for key in required_in_production if not getattr(self, key, None)]
                if missing:
                    raise ValueError(f"Missing required production settings: {missing}")
                
                if not has_llm_key:
                    raise ValueError("No LLM provider API key configured")
                    
                if not has_media_config:
                    raise ValueError("No media provider API keys configured")
    
    # Instantiate and validate
    settings = EnvSettings()
    settings.validate_required_settings()
    return settings


# Create global settings instance
settings = get_settings()

# Mask secret for logging
def mask_secret(text: str, secret: Optional[str] = None) -> str:
    """Masks secret API keys in log messages and error tracebacks."""
    if not text:
        return text
    secrets_to_mask = [secret] if secret else []
    for key_env in ["GEMINI_API_KEY", "OPENAI_API_KEY", "KIMI_API_KEY", 
                   "STORY_API_KEY", "IMAGE_API_KEY", "TTS_API_KEY",
                   "STABLE_AUDIO_API_KEY", "STABILITY_API_KEY",
                   "REPLICATE_API_KEY", "ELEVENLABS_API_KEY",
                   "SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_URL",
                   "SECRET_KEY", "HF_API_TOKEN"]:
        val = os.getenv(key_env) or getattr(settings, key_env, "")
        if val:
            secrets_to_mask.append(val)

    masked_text = str(text)
    for s in secrets_to_mask:
        if s and len(s) > 4:
            masked = f"{s[:3]}...{s[-4:]}"
            masked_text = masked_text.replace(s, masked)
    return masked_text
