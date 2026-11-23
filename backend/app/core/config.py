import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "BMIR 2.0 - Bharat Multisector Innovation & Research"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "bmir-enterprise-secure-ai-research-platform-secret-key-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours for seamless research sessions
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Organization Credentials & Identity
    FOUNDER_NAME: str = "Binod Pandey"
    FOUNDER_EMAIL: str = "binod.pandey@bmirresearch.in"
    ADMIN_EMAIL: str = "admin@bmirresearch.in"
    DEFAULT_INITIAL_PASSWORD: str = "Bmir@2026!Enterprise"
    BMIR_LOCATION: str = "Bhagalpur, Bihar, India"
    BMIR_PHONE: str = "+91 8340 328914"
    BMIR_WEBSITE: str = "https://bmirresearch.in"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./bmir_platform.db"

    # Redis (optional fallback in-memory)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Storage
    STORAGE_BACKEND: str = "local"  # 'local' or 's3'
    LOCAL_STORAGE_PATH: str = "./uploads"
    S3_BUCKET_NAME: str = ""
    S3_REGION: str = ""
    S3_ACCESS_KEY_ID: str = ""
    S3_SECRET_ACCESS_KEY: str = ""

    # AI Configuration
    PREFERRED_AI_PROVIDER: str = "gemini"  # 'gemini', 'openai', 'anthropic', or 'mock_fallback'
    OPENAI_API_KEY: str = ""
    OPENAI_DEFAULT_MODEL: str = "gpt-4o"
    GEMINI_API_KEY: str = ""
    GEMINI_DEFAULT_MODEL: str = "gemini-1.5-pro"
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_DEFAULT_MODEL: str = "claude-3-5-sonnet-20241022"

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )


settings = Settings()

