"""Configuration management for FastAPI application using Pydantic Settings.

Classes:
    Settings: Loads and manages application settings from environment variables or a .env file.
"""
from functools import lru_cache

from pydantic import computed_field, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    SECRET_KEY: str = Field("default_secret_key", validation_alias='SECRET_KEY')  # noqa S105
    ALGORITHM: str = Field("HS256", validation_alias='ALGORITHM')
    EXPIRES_IN: int = Field(3600, validation_alias='EXPIRES_IN')  # 60 minutes
    REFRESH_TOKEN_EXPIRES_IN: int = Field(604800, validation_alias='REFRESH_TOKEN_EXPIRES_IN')  # 7 days
    RESET_PASSWORD_EXPIRES_IN: int = Field(3600, validation_alias='RESET_PASSWORD_EXPIRES_IN')  # 60 minutes
    ACTIVE_ACCOUNT_EXPIRES_IN: int = Field(3600, validation_alias='ACTIVE_ACCOUNT_EXPIRES_IN')  # 60 minutes


class BcryptSettings(BaseSettings):
    SALT_ROUNDS: int = Field(12, validation_alias='SALT_ROUNDS')


class DbSettings(BaseSettings):
    # MySQL or PostgresSQL
    DB_HOST: str | None = Field(validation_alias='DB_HOST')
    DB_NAME: str | None = Field(validation_alias='DB_NAME')
    DB_USER: str | None = Field(validation_alias='DB_USER')
    DB_PASSWORD: str | None = Field(validation_alias='DB_PASSWORD')
    DB_ENGINE: str | None = Field(validation_alias='DB_ENGINE')
    DB_POOL_SIZE: int = Field(10, validation_alias='DB_POOL_SIZE')

    # MongoDB
    MONGO_INITDB_ROOT_USERNAME: str | None = Field(validation_alias='MONGO_INITDB_ROOT_USERNAME')
    MONGO_INITDB_ROOT_PASSWORD: str | None = Field(validation_alias='MONGO_INITDB_ROOT_PASSWORD')
    MONGO_HOST: str | None = Field(validation_alias='MONGO_HOST')
    MONGO_PORT: int | None = Field(validation_alias='MONGO_PORT')
    MONGO_INITDB_DATABASE: str | None = Field(validation_alias='MONGO_INITDB_DATABASE')

    @computed_field
    @property
    def SQL_CLIENT_URL(self) -> str:
        return f"{self.DB_ENGINE}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}/{self.DB_NAME}"

    @computed_field
    @property
    def MONGO_CLIENT_URL(self) -> str:
        return (
            f"mongodb://{self.MONGO_INITDB_ROOT_USERNAME}:{self.MONGO_INITDB_ROOT_PASSWORD}@"
            f"{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_INITDB_DATABASE}"
            "?directConnection=true&authSource=admin"
        )

    @computed_field
    @property
    def AGENDA_DB_ADDRESS(self) -> str:
        return (
            f"mongodb://{self.MONGO_INITDB_ROOT_USERNAME}:{self.MONGO_INITDB_ROOT_PASSWORD}@"
            f"{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_INITDB_DATABASE}"
        )


class MinioSettings(BaseSettings):
    MINIO_HOST: str | None = Field(validation_alias='MINIO_HOST')
    MINIO_PORT: int | None = Field(validation_alias='MINIO_PORT')
    MINIO_USE_SSL: bool | None = Field(validation_alias='MINIO_USE_SSL')
    MINIO_ACCESS_KEY: str | None = Field(validation_alias='MINIO_ACCESS_KEY')
    MINIO_SECRET_KEY: str | None = Field(validation_alias='MINIO_SECRET_KEY')


class MailSettings(BaseSettings):
    MAIL_HOST: str | None = Field(validation_alias='MAIL_HOST')
    MAIL_PORT: int | None = Field(validation_alias='MAIL_PORT')
    MAIL_USER: str | None = Field(validation_alias='MAIL_USER')
    MAIL_PASSWORD: str | None = Field(validation_alias='MAIL_PASSWORD')
    MAIL_FROM: str | None = Field(validation_alias='MAIL_FROM')


class TimezoneSettings(BaseSettings):
    TZ: str = Field("Asia/Ho_Chi_Minh", validation_alias='TZ')


class ApiSettings(BaseSettings):
    URL: str = Field("http://localhost:8000", validation_alias='URL')


class AppSettings(BaseSettings):
    NAME: str = Field("FastAPI Project", validation_alias='NAME')


class PagingSettings(BaseSettings):
    DEFAULT_PAGE_SIZE: int = Field(10, validation_alias='DEFAULT_PAGE_SIZE')


class LoggingSettings(BaseSettings):
    LOG_LEVEL: str = Field("DEBUG", validation_alias='LOG_LEVEL')
    LOGSTASH_HOST: str | None = Field(validation_alias='LOGSTASH_HOST')
    LOGSTASH_PORT: int | None = Field(validation_alias='LOGSTASH_PORT')
    GOOGLE_CHAT_WEBHOOK: str | None = Field(validation_alias='GOOGLE_CHAT_WEBHOOK')


class Settings(BaseSettings):
    """Manages application settings using Pydantic, loading from environment variables or a .env file."""
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    db: DbSettings = Field(default_factory=DbSettings)
    minio: MinioSettings = Field(default_factory=MinioSettings)
    auth: AuthSettings = Field(default_factory=AuthSettings)
    bcrypt: BcryptSettings = Field(default_factory=BcryptSettings)
    mail: MailSettings = Field(default_factory=MailSettings)
    timezone: TimezoneSettings = Field(default_factory=TimezoneSettings)
    api: ApiSettings = Field(default_factory=ApiSettings)
    app: AppSettings = Field(default_factory=AppSettings)
    paging: PagingSettings = Field(default_factory=PagingSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)

    # Environment
    DEBUG_MODE: bool = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = Settings()
