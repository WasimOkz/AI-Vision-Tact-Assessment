"""
Backend Configuration Module
Environment-based configuration using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "AI Candidate Assessment Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # LLM Configuration - Groq
    GROQ_API_KEY: str = ""
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    
    # Redis (optional)
    REDIS_URL: Optional[str] = None
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Voice Services (optional - using browser-based fallback)
    ELEVENLABS_API_KEY: Optional[str] = None
    DEEPGRAM_API_KEY: Optional[str] = None
    
    # Avatar Services
    DID_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
