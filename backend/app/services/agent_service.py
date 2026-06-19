from __future__ import annotations

import base64
import json
import logging
import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from time import perf_counter
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field
from pydantic_ai import Agent, RunContext

from app.core.client_factory import create_llm_client
from app.core.config import get_agent_api_key, settings
from app.core.image_resolver import image_to_photo
from app.core.logging_config import configure_logging, summarize_for_log, summarize_text
from app.core.prompt_loader import load_prompt
from app.schemas.story_elements import Image, Scene, StoryState, UserAction


configure_logging(log_level=settings.log_level, log_file=settings.log_file)
logger = logging.getLogger(__name__)


@dataclass
class StoryAgentDeps:
    state: StoryState
    action: UserAction
    scene: Scene = field(default_factory=Scene)


class TurnComplete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str = Field(
        default="Ya hay suficiente material para construir el siguiente turno del cuento.",
        description="Motivo por el que el agente considera completo este turno.",
    )


def _configure_provider_environment(*, require_api_key: bool = False) -> None:
    if settings.agent_api_key and "OPENAI_API_KEY" not in os.environ:
        os.environ["OPENAI_API_KEY"] = settings.agent_api_key

    if settings.base_url and "OPENAI_BASE_URL" not in os.environ:
        os.environ["OPENAI_BASE_URL"] = settings.base_url

    if require_api_key and "OPENAI_API_KEY" not in os.environ:
        os.environ["OPENAI_API_KEY"] = get_agent_api_key()


def _agent_model() -> str:
    if ":" in settings.agent_model:
        return settings.agent_model

    return f"openai-chat:{settings.agent_model}"


@lru_cache
def get_story_agent() -> Agent:
    _configure_provider_environment(require_api_key=True)

    agent = Agent(
        _agent_model(),
        deps_type=StoryAgentDeps,
        output_type=TurnComplete,
        instructions=load_prompt("story_agent.txt"),
    )

    @agent.instructions
    def add_story_context(ctx: RunContext[StoryAgentDeps]) -> str:
        return json.dumps(
            {
                "state": ctx.deps.state.model_dump(mode="json"),
                "user_action": ctx.deps.action.model_dump(mode="json"),
                "generated_scene_so_far": ctx.deps.scene.model_dump(mode="json"),
            },
            ensure_ascii=False,
        )

    @agent.tool
    def generate_text(
        ctx: RunContext[StoryAgentDeps],
        brief: str,
        tone: str = "infantil, cálido y claro",
    ) -> str:
        """Escribe un fragmento narrativo para el siguiente turno del cuento."""
        content = _generate_text(brief=brief, tone=tone)
        _append_text(ctx.deps.scene, content)
        return content

    @agent.tool
    def analyze_image(
        ctx: RunContext[StoryAgentDeps],
        image: Image | None = None,
        question: str = "Describe la imagen para continuar el cuento.",
    ) -> str:
        """Analiza una imagen disponible en la historia o subida por el usuario."""
        selected_image = image or _image_from_action(ctx.deps.action)

        if selected_image is None:
            raise ValueError("No image was provided and the user action does not contain an image.")

        return _analyze_image(image=selected_image, question=question)

    @agent.tool
    def generate_image(
        ctx: RunContext[StoryAgentDeps],
        prompt: str,
        scene_text: str | None = None,
    ) -> Image:
        """Prepara una ilustración infantil basada en una descripcion visual."""
        image = _generate_image(prompt=prompt, scene_text=scene_text)
        _append_image(ctx.deps.scene, image)
        return image

    return agent


async def run_story_turn(state: StoryState, action: UserAction) -> Scene:
    deps = StoryAgentDeps(state=state, action=action)
    start = perf_counter()

    logger.info(
        "agent_service.start story_id=%s model=%s action=%s",
        state.story_id,
        _agent_model(),
        summarize_for_log(action, include_payloads=settings.log_llm_payloads),
    )

    result = await get_story_agent().run(
        "Prepara el siguiente turno de la historia.",
        deps=deps,
    )

    _ensure_scene_has_material(deps.scene)

    logger.info(
        "agent_service.end story_id=%s duration_ms=%s reason=%s scene_texts=%s scene_images=%s",
        state.story_id,
        int((perf_counter() - start) * 1_000),
        summarize_text(result.output.reason),
        _count_items(deps.scene.texts),
        _count_items(deps.scene.images),
    )

    return deps.scene


def run_story_turn_sync(state: StoryState, action: UserAction) -> Scene:
    deps = StoryAgentDeps(state=state, action=action)
    start = perf_counter()

    logger.info(
        "agent_service.start story_id=%s model=%s action=%s",
        state.story_id,
        _agent_model(),
        summarize_for_log(action, include_payloads=settings.log_llm_payloads),
    )

    result = get_story_agent().run_sync(
        "Prepara el siguiente turno de la historia.",
        deps=deps,
    )

    _ensure_scene_has_material(deps.scene)

    logger.info(
        "agent_service.end story_id=%s duration_ms=%s reason=%s scene_texts=%s scene_images=%s",
        state.story_id,
        int((perf_counter() - start) * 1_000),
        summarize_text(result.output.reason),
        _count_items(deps.scene.texts),
        _count_items(deps.scene.images),
    )

    return deps.scene


def _generate_text(*, brief: str, tone: str) -> str:
    start = perf_counter()
    logger.info(
        "tool.generate_text.start brief=%s tone=%s",
        summarize_text(brief),
        summarize_text(tone),
    )

    prompt = load_prompt(
        "generate_text.txt",
        brief=brief,
        tone=tone,
    )

    response = _llm_client().chat.completions.create(
        model=settings.model_name,
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": "Escribe el siguiente fragmento del cuento.",
            },
        ],
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError("generate_text returned empty content.")

    logger.info(
        "tool.generate_text.end duration_ms=%s content_length=%s",
        int((perf_counter() - start) * 1_000),
        len(content),
    )

    return content


def _analyze_image(*, image: Image, question: str) -> str:
    start = perf_counter()
    logger.info(
        "tool.analyze_image.start image=%s question=%s",
        summarize_for_log(image, include_payloads=settings.log_llm_payloads),
        summarize_text(question),
    )

    image_bytes = image_to_photo(image=image)
    image_content = _build_image_content(image=image, image_bytes=image_bytes)
    mime_type = _guess_mime_type(image)
    prompt = load_prompt(
        "analyze_image.txt",
        question=question,
    )

    response = _llm_client().chat.completions.create(
        model=settings.model_name,
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": question,
                    },
                    image_content,
                ],
            },
        ],
    )

    description = response.choices[0].message.content

    if not description:
        raise RuntimeError("analyze_image returned empty content.")

    image.description = description

    logger.info(
        "tool.analyze_image.end duration_ms=%s mime_type=%s description_length=%s",
        int((perf_counter() - start) * 1_000),
        mime_type,
        len(description),
    )

    return description


def _generate_image(*, prompt: str, scene_text: str | None) -> Image:
    start = perf_counter()
    logger.info(
        "tool.generate_image.start prompt=%s scene_text=%s",
        summarize_text(prompt),
        summarize_text(scene_text),
    )

    final_prompt = load_prompt(
        "generate_image.txt",
        prompt=prompt,
        scene_text=scene_text or "",
    )

    image = Image(
        image_id=f"img_{uuid4().hex}",
        url=None,
        path=None,
        prompt=final_prompt,
        description=prompt,
    )

    logger.info(
        "tool.generate_image.end duration_ms=%s image_id=%s prompt_length=%s",
        int((perf_counter() - start) * 1_000),
        image.image_id,
        len(final_prompt),
    )

    return image


def _llm_client():
    return create_llm_client(
        api_key=get_agent_api_key(),
        base_url=settings.base_url,
    )


def _build_image_content(*, image: Image, image_bytes: bytes) -> dict[str, Any]:
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    mime_type = _guess_mime_type(image)

    return {
        "type": "image_url",
        "image_url": {
            "url": f"data:{mime_type};base64,{encoded}",
        },
    }


def _guess_mime_type(image: Image) -> str:
    if image.path is None:
        return "image/png"

    suffix = Path(image.path).suffix.lower()

    match suffix:
        case ".jpg" | ".jpeg":
            return "image/jpeg"
        case ".png":
            return "image/png"
        case ".webp":
            return "image/webp"
        case _:
            raise ValueError(f"Unsupported image extension: {suffix}")


def _image_from_action(action: UserAction) -> Image | None:
    if isinstance(action.user_action, Image):
        return action.user_action

    return None


def _append_text(scene: Scene, content: str) -> None:
    if isinstance(scene.texts, list):
        scene.texts.append(content)
        return

    scene.texts = [scene.texts, content] if scene.texts else [content]


def _append_image(scene: Scene, image: Image) -> None:
    if isinstance(scene.images, list):
        scene.images.append(image)
        return

    scene.images = [scene.images, image] if scene.images else [image]


def _ensure_scene_has_material(scene: Scene) -> None:
    if _count_items(scene.texts) > 0 or _count_items(scene.images) > 0:
        return

    raise RuntimeError("Agent finished without generated material.")


def _count_items(value: Any) -> int:
    if value is None:
        return 0

    if isinstance(value, list):
        return len(value)

    return 1
