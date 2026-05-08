from __future__ import annotations

import json

from backend.utils.client_factory import create_llm_client
from backend.utils.config import get_settings
from openai import OpenAI
from backend.utils.prompt_loader import load_prompt
from backend.schemas import Scene, StoryState

settings = get_settings()


def write_scene(
    state: StoryState,
    brief: str,
    tone: str | None = None,
) -> Scene:
    
    client = create_llm_client(
        api_key=settings.api_key.get_secret_value(),
        base_url=settings.base_url,
    )
    
    prompt = load_prompt(
        "write_scene.txt",
        state_json=state.model_dump_json(indent=2),
        brief=brief,
        tone=tone or "calido, imaginativo y apropiado para ninos",
    )

    messages = [
        {"role": "system", "content": "Devuelve unicamente JSON valido para el schema pedido."},
        {"role": "user", "content": prompt},
    ]

    response = client.chat.completions.create(
        model=settings.model_name,
        messages=messages,
    )

    raw_content = response.choices[0].message.content or ""

    try:
        return _parse_scene_json(raw_content)
    except ValueError:
        retry_messages = messages + [
            {"role": "assistant", "content": raw_content},
            {
                "role": "user",
                "content": (
                    "Tu respuesta anterior no fue JSON valido con la forma exacta "
                    '{"title": "...", "content": "..."}. '
                    "Devuelve solo JSON valido, sin markdown ni texto extra."
                ),
            },
        ]

        retry_response = client.chat.completions.create(
            model=settings.model_name,
            messages=retry_messages,
        )
        retry_content = retry_response.choices[0].message.content or ""
        return _parse_scene_json(retry_content)


def _parse_scene_json(raw_content: str) -> Scene:
    candidate = raw_content.strip()
    if candidate.startswith("```"):
        lines = candidate.splitlines()
        if len(lines) >= 3:
            candidate = "\n".join(lines[1:-1]).strip()

    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise ValueError("Model did not return valid JSON for Scene.") from exc

    return Scene.model_validate(parsed)
