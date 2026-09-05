import os
from typing import List, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Assisted Code Review & Testing Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Security & JWT
    SECRET_KEY: str = "SUPER_SECRET_PRODUCTION_KEY_CHANGE_IN_ENV_32_CHARS_MIN!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database
    DATABASE_URL: str = "sqlite:///./code_review.db"  # Defaults to SQLite for easy local dev, configurable to Postgres in prod

    # OpenAI API
    OPENAI_API_KEY: str = "mock"  # Defaults to 'mock' if not set for testing
    OPENAI_MODEL: str = "gpt-4o-mini"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 20

    # Sandboxed Execution Settings
    SANDBOX_TIMEOUT_SECONDS: int = 5
    SANDBOX_MAX_MEMORY_MB: int = 128

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
