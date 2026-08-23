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

    # Comma-separated browser origins permitted to call the API.
    cors_origins: str = (
        "http://localhost:3000,"
        "http://127.0.0.1:3000"
    )

    # ==============================
    # Environment Configuration
    # ==============================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
