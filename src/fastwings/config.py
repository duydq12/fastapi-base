"""Configuration management for FastAPI application using Pydantic Settings.

Classes:
    Settings: Loads and manages application settings from environment variables or a .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Manages application settings using Pydantic, loading from environment variables or a .env file."""
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    # Environment
    LOG_LEVEL: str = "DEBUG"
    DEBUG_MODE: bool = True

    # Basic Auth
    BASIC_USERNAME: str | None = None
    BASIC_PASSWORD: str | None = None

    # Bearer Auth (JWT)
    SECRET_KEY: str = "a_very_secret_key_that_should_be_changed"  # noqa S105
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 30  # 30 minutes

    # Database
    DB_HOST: str | None = None
    DB_NAME: str | None = None
    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    DB_ENGINE: str | None = None
    DB_POOL_SIZE: int = 10

    # Logstash
    LOGSTASH_HOST: str | None = None
    LOGSTASH_PORT: int | None = None

    # Google Chat
    GOOGLE_CHAT_WEBHOOK: str | None = None


# Tạo một instance duy nhất để sử dụng trong toàn bộ ứng dụng
settings = Settings()
