"""
CaseSync Configuration Module
Handles all application configuration using Pydantic Settings.
Environment variables can override default values.
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Default values provided for local development.
    """
    
    # Application metadata
    APP_NAME: str = "CaseSync"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database configuration
    # Format: postgresql://user:password@host:port/database
    # SQLite fallback for development: sqlite:///./casesync.db
    DATABASE_URL: str = "sqlite:///./casesync.db"
    
    # CORS settings for frontend access
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # File upload settings
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_AUDIO_TYPES: List[str] = [
        "audio/wav", "audio/mpeg", "audio/mp3", "audio/mp4",
        "audio/x-m4a", "audio/webm", "audio/ogg"
    ]
    
    # Deepgram API settings
    DEEPGRAM_API_KEY: str  # Must be set via environment variable (.env file)
    DEEPGRAM_API_URL: str = "https://api.deepgram.com/v1/listen"
    
    # NER model for multilingual entity extraction
    NER_MODEL: str = "bert-base-multilingual-cased"
    
    # Speech-to-text settings
    # Supported languages for Deepgram
    SUPPORTED_LANGUAGES: List[str] = ["en", "hi"]
    DEFAULT_LANGUAGE: str = "en"
    
    # PDF generation settings
    PDF_OUTPUT_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pdfs")
    
    # Hindi font path for PDF generation (Noto Sans Devanagari)
    HINDI_FONT_PATH: str = ""  # Will be set during initialization
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from old .env files


# Global settings instance
settings = Settings()

# Ensure upload and PDF directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.PDF_OUTPUT_DIR, exist_ok=True)
