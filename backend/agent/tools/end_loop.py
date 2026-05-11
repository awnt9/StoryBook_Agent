from __future__ import annotations

import logging

from backend.schemas.tool_args import EndLoopArgs
from backend.utils.config import get_settings
from backend.utils.logging_config import configure_logging, summarize_text


settings = get_settings()
configure_logging(log_level=settings.log_level, log_file=settings.log_file)
logger = logging.getLogger(__name__)


def end_loop(*, args: EndLoopArgs) -> dict:
    logger.info("tool.end_loop reason=%s", summarize_text(args.reason))

    return {
        "type": "end_loop",
        "reason": args.reason,
    }
    
