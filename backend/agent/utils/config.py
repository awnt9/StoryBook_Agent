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
    log_level: str = "INFO"
    log_llm_payloads: bool = False
    log_file: str | None = None


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


def _get_env_value(env_values: dict[str, str], key: str) -> str | None:
    value = os.getenv(key)
    if value is not None:
        return value

    return env_values.get(key)


def _parse_bool(value: str | None, *, default: bool = False) -> bool:
    if value is None or value == "":
        return default

    match value.strip().lower():
        case "1" | "true" | "yes" | "y" | "on":
            return True
        case "0" | "false" | "no" | "n" | "off":
            return False
        case _:
            raise ValueError(f"Invalid boolean value: {value}")


@lru_cache
def get_settings() -> Settings:
    env_values = _load_env_file(ROOT_DIR / ".env")
    api_key = _get_env_value(env_values, "API_KEY")
    base_url = _get_env_value(env_values, "BASE_URL")
    model_name = _get_env_value(env_values, "MODEL_NAME") or "Hermes-4.3-36B"
    log_level = _get_env_value(env_values, "LOG_LEVEL") or "INFO"
    log_llm_payloads = _parse_bool(_get_env_value(env_values, "LOG_LLM_PAYLOADS"))
    log_file = _get_env_value(env_values, "LOG_FILE") or None

    if not api_key:
        raise ValueError("API_KEY is missing from the environment and .env file.")

    return Settings(
        api_key=SecretStr(api_key),
        base_url=base_url,
        model_name=model_name,
        log_level=log_level,
        log_llm_payloads=log_llm_payloads,
        log_file=log_file,
    )
