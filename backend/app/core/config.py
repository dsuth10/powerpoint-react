from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    JWT_SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_HOURS: int = 24
    PROJECT_ENV: str = "development"

    # API key access (optional key-only mode)
    # If REQUIRE_API_KEY is true and API_KEYS has at least one value,
    # HTTP routes (except health/auth) and WebSocket connections will require a valid key.
    REQUIRE_API_KEY: bool = False
    API_KEYS: List[str] = []

    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]

    # LLM / OpenRouter configuration
    OPENROUTER_API_KEY: str | None = None
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_TIMEOUT_SECONDS: int = 30
    OPENROUTER_DEFAULT_MODEL: str = "openai/gpt-4o-mini"
    OPENROUTER_ALLOWED_MODELS: List[str] = [
        "openai/gpt-4o-mini",
        "openai/gpt-4o",
    ]
    # Optional headers recommended by OpenRouter
    OPENROUTER_HTTP_REFERER: str | None = None  # e.g., your site/repo URL
    OPENROUTER_APP_TITLE: str | None = None     # e.g., "AI PowerPoint Generator"
    # Test/ops flag: when true, do not silently fall back; raise on upstream failure
    OPENROUTER_REQUIRE_UPSTREAM: bool = False
    LLM_LOG_PROMPTS: bool = False

    # Stability AI configuration
    STABILITY_API_KEY: str | None = None
    STABILITY_BASE_URL: str = "https://api.stability.ai"
    STABILITY_TIMEOUT_SECONDS: int = 30
    STABILITY_PLACEHOLDER_URL: str = "https://placehold.co/600x400"

    # Public/base URLs and static files
    PUBLIC_BASE_URL: str = "http://localhost:8000"
    STATIC_URL_PATH: str = "/static"
    STATIC_DIR: str = "/app/static"
    STATIC_IMAGES_SUBDIR: str = "images"

    # Image service behaviors
    IMAGE_CACHE_TTL_SECONDS: int = 1800  # 30 minutes
    IMAGE_CACHE_MAX_ENTRIES: int = 256
    IMAGE_MAX_CONCURRENCY: int = 4

    # PPTX builder settings
    PPTX_TEMPLATE_PATH: str | None = None
    PPTX_TEMP_DIR: str = "/tmp"
    PPTX_FONT_NAME: str = "Calibri"
    PPTX_TITLE_FONT_SIZE_PT: int = 32
    PPTX_BODY_FONT_SIZE_PT: int = 18
    PPTX_IMAGE_MAX_WIDTH_IN: float = 8.0
    PPTX_IMAGE_MAX_HEIGHT_IN: float = 4.5
    PPTX_IMAGE_HTTP_TIMEOUT_SECONDS: int = 10

    class Config:
        env_file = ".env"

settings = Settings() 