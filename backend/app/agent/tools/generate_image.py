from __future__ import annotations

import logging
from time import perf_counter
from uuid import uuid4

from backend.agent.schemas.objects import Image
from backend.agent.schemas.tool_args import GenerateImageArgs
from backend.agent.utils.config import get_settings
from backend.agent.utils.logging_config import configure_logging, summarize_text
from backend.agent.utils.prompt_loader import load_prompt


settings = get_settings()
configure_logging(log_level=settings.log_level, log_file=settings.log_file)
logger = logging.getLogger(__name__)


def generate_image(
    *,
    args: GenerateImageArgs,
) -> dict:
    start = perf_counter()
    logger.info(
        "tool.generate_image.start prompt=%s scene_text=%s",
        summarize_text(args.prompt),
        summarize_text(args.scene_text),
    )

    final_prompt = load_prompt(
        "generate_image.txt",
        prompt=args.prompt,
        scene_text=args.scene_text or "",
    )

    image = Image(
        image_id=f"img_{uuid4().hex}",
        url=None,
        path=None,
        prompt=final_prompt,
        description=args.prompt,
    )

    logger.info(
        "tool.generate_image.end duration_ms=%s image_id=%s prompt_length=%s",
        int((perf_counter() - start) * 1_000),
        image.image_id,
        len(final_prompt),
    )

    return {
        "type": "image",
        "image": image.model_dump(mode="json"),
    }
