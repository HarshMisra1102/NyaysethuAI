from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ==============================
    # Database
    # ==============================
    database_url: str

    # ==============================
    # JWT Authentication
    # ==============================
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    # ==============================
    # AI / Gemini
    # ==============================
    gemini_api_key: str

    # ==============================
    # Environment Configuration
    # ==============================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()