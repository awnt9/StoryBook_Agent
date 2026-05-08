from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, SecretStr


ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseModel):
    api_key: SecretStr
    base_url: str | None = None
    model_name: str = "Hermes-4.3-36B"


def _load_env_file(env_path: Path) -> dict[str, str]:
    if not env_path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")

    return values


@lru_cache
def get_settings() -> Settings:
    env_values = _load_env_file(ROOT_DIR / ".env")
    api_key = os.getenv("API_KEY") or env_values.get("API_KEY")
    base_url = os.getenv("BASE_URL") or env_values.get("BASE_URL")
    model_name = os.getenv("MODEL_NAME") or env_values.get("MODEL_NAME") or "Hermes-4.3-36B"

    if not api_key:
        raise ValueError("API_KEY is missing from the environment and .env file.")

    return Settings(
        api_key=SecretStr(api_key),
        base_url=base_url,
        model_name=model_name,
    )
