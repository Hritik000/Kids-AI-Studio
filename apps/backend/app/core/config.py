import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "KidsAI Studio API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENV: str = "development"
    
    # AI API Keys & Endpoints (Configurable via env)
    STORY_API_KEY: str = ""
    IMAGE_API_KEY: str = ""
    TTS_API_KEY: str = ""
    
    # Supabase & Storage
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    R2_BUCKET_URL: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
