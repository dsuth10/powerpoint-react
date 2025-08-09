from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    JWT_SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_HOURS: int = 24
    PROJECT_ENV: str = "development"

    # LLM / OpenRouter configuration
    OPENROUTER_API_KEY: str | None = None
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_TIMEOUT_SECONDS: int = 30
    OPENROUTER_DEFAULT_MODEL: str = "openrouter/gpt-4o-mini"
    OPENROUTER_ALLOWED_MODELS: List[str] = [
        "openrouter/gpt-4o-mini",
        "openrouter/gpt-4o",
    ]
    LLM_LOG_PROMPTS: bool = False

    # Stability AI configuration
    STABILITY_API_KEY: str | None = None
    STABILITY_BASE_URL: str = "https://api.stability.ai/v2"
    STABILITY_TIMEOUT_SECONDS: int = 30
    STABILITY_PLACEHOLDER_URL: str = "https://placehold.co/600x400"

    # Image service behaviors
    IMAGE_CACHE_TTL_SECONDS: int = 1800  # 30 minutes
    IMAGE_CACHE_MAX_ENTRIES: int = 256
    IMAGE_MAX_CONCURRENCY: int = 4

    class Config:
        env_file = ".env"

settings = Settings() 