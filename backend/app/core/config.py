from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "StoryBook Agent Backend"
    environment: str = "development"
    debug: bool = True

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    database_url: str

    cors_origins: str = "http://localhost:3000"

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    refresh_token_cookie_name: str = "refresh_token"
    cookie_secure: bool = False
    cookie_samesite: str = "lax"

    agent_max_iterations: int = 4
    log_level: str = "INFO"
    log_llm_payloads: bool = False
    log_file: str | None = None

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
