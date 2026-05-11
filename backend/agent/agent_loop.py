from __future__ import annotations

import json
import logging
from time import perf_counter
from typing import Any

from backend.agent.utils.config import get_settings
from backend.agent.utils.client_factory import create_llm_client
from backend.agent.utils.logging_config import configure_logging, summarize_for_log, summarize_text
from backend.agent.utils.prompt_loader import load_prompt

from backend.agent.schemas.objects import (
    Scene, 
    StoryState,
    ToolCallRecord, 
    UserAction, 
    ToolHistory,
    Image,
    )

from backend.agent.schemas.tool_args import (
    GenerateTextArgs,
    AnalyzeImageArgs,
    GenerateImageArgs,
    EndLoopArgs,
)

from backend.agent.tools.generate_text import generate_text
from backend.agent.tools.analyze_image import analyze_image
from backend.agent.tools.generate_image import generate_image
from backend.agent.tools.end_loop import end_loop 

settings = get_settings()
configure_logging(log_level=settings.log_level, log_file=settings.log_file)
logger = logging.getLogger(__name__)

AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "generate_text",
            "description": "Escribe un fragmento narrativo para el siguiente turno del cuento.",
            "parameters": GenerateTextArgs.model_json_schema(),
            "strict": False,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_image",
            "description": "Analiza una imagen disponible en la historia o subida por el usuario.",
            "parameters": AnalyzeImageArgs.model_json_schema(),
            "strict": False,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_image",
            "description": "Genera una imagen o ilustración basada en una descripción.",
            "parameters": GenerateImageArgs.model_json_schema(),
            "strict": False,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "end_loop",
            "description": "Finaliza el bucle del agente cuando ya hay suficiente material.",
            "parameters": EndLoopArgs.model_json_schema(),
            "strict": False,
        },
    },
]

def run_agent_loop(state: StoryState, action: UserAction) -> Scene:
    iteration = 0
    selected_tool_name: str | None = None

    logger.info(
        "agent_loop.start story_id=%s model=%s action=%s",
        state.story_id,
        settings.model_name,
        _summarize_user_action(action),
    )

    try:
        client = create_llm_client(
            api_key=settings.api_key.get_secret_value(),
            base_url=settings.base_url,
        )

        working_scene = Scene()
        tool_history = ToolHistory()

        while True:
            iteration += 1
            logger.info(
                "agent_loop.iteration.start iteration=%s history_calls=%s scene_texts=%s scene_images=%s",
                iteration,
                len(tool_history.calls),
                _count_items(working_scene.texts),
                _count_items(working_scene.images),
            )

            messages: list[dict[str, Any]] = [
                {
                    "role": "system",
                    "content": load_prompt("run_agent_loop.txt"),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "task": "Prepara el siguiente turno de la historia.",
                            "state": state.model_dump(mode="json"),
                            "user_action": action.model_dump(mode="json"),
                            "tool_history": tool_history.model_dump(mode="json") if tool_history else None,
                        },
                        ensure_ascii=False,
                    ),
                },
            ]

            response = client.chat.completions.create(
                model=settings.model_name,
                messages=messages,
                tools=AGENT_TOOLS,
                tool_choice="auto",
                parallel_tool_calls=False,
            )

            assistant_message = response.choices[0].message
            tool_calls = assistant_message.tool_calls

            if not tool_calls:
                raise RuntimeError("Agent did not return a tool call.")

            tool_call = tool_calls[0]
            selected_tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            logger.info(
                "tool.selected iteration=%s tool=%s arguments=%s",
                iteration,
                selected_tool_name,
                summarize_for_log(
                    arguments,
                    include_payloads=settings.log_llm_payloads,
                ),
            )

            tool_start = perf_counter()
            logger.info("tool.execution.start iteration=%s tool=%s", iteration, selected_tool_name)
            try:
                output_payload = _execute_tool(tool_name=selected_tool_name, arguments=arguments)
            except Exception:
                logger.exception(
                    "tool.execution.error iteration=%s tool=%s arguments=%s",
                    iteration,
                    selected_tool_name,
                    summarize_for_log(
                        arguments,
                        include_payloads=settings.log_llm_payloads,
                    ),
                )
                raise

            tool_history.calls.append(
                ToolCallRecord(
                    tool_name=selected_tool_name,
                    arguments=arguments,
                    output=output_payload,
                )
            )

            output_type = output_payload.get("type")
            should_stop = False

            match output_type:
                case "text" | "image_analysis":
                    working_scene.texts.append(output_payload)
                case "image":
                    working_scene.images.append(output_payload)
                case "end_loop":
                    should_stop = True

            logger.info(
                "tool.execution.end iteration=%s tool=%s output_type=%s scene_texts=%s scene_images=%s",
                iteration,
                selected_tool_name,
                output_type,
                _count_items(working_scene.texts),
                _count_items(working_scene.images),
            )

            if should_stop:
                logger.info(
                    "agent_loop.end_loop_selected iteration=%s reason=%s",
                    iteration,
                    summarize_text(output_payload.get("reason")),
                )
                break

        logger.info(
            "agent_loop.end story_id=%s iterations=%s scene_texts=%s scene_images=%s",
            state.story_id,
            iteration,
            _count_items(working_scene.texts),
            _count_items(working_scene.images),
        )
        return working_scene
    except Exception:
        logger.exception(
            "agent_loop.error story_id=%s iteration=%s selected_tool=%s",
            state.story_id,
            iteration,
            selected_tool_name,
        )
        raise

def _execute_tool(
    *,
    tool_name: str,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    match tool_name:
        case "generate_text":
            args = GenerateTextArgs.model_validate(arguments)
            return generate_text(
                args=args,
            )

        case "analyze_image":
            args = AnalyzeImageArgs.model_validate(arguments)
            return analyze_image(
                args=args,
            )

        case "generate_image":
            args = GenerateImageArgs.model_validate(arguments)
            return generate_image(
                args=args,
            )

        case "end_loop":
            args = EndLoopArgs.model_validate(arguments)
            return end_loop(args=args)

        case _:
            raise ValueError(f"Unknown tool: {tool_name}")


def _count_items(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, list):
        return len(value)

    return 1


def _summarize_user_action(action: UserAction) -> Any:
    return summarize_for_log(
        action.model_dump(mode="json"),
        include_payloads=settings.log_llm_payloads,
    )

if __name__ == "__main__":
    initial_image = Image(
        image_id="img_test_001",
        path="C:\\Users\\antonio\\Desktop\\Master\\modulo10\\tasks\\challenge_task\\images\\img_test_001.png",
        url=None,
        prompt=None,
        description=None,
    )

    initial_scene = Scene(
        images=[
            initial_image,
        ],
    )

    state = StoryState(
        story_id="story_test_001",
        current_scene=initial_scene,
        history=[
            initial_scene,
        ],
    )

    action = UserAction(
        user_action="Continúa el cuento. Nilo debe encontrar un objeto mágico y aprender una pequeña lección."
    )

    result_scene = run_agent_loop(
        state=state,
        action=action,
    )

    print("\n=== RESULT SCENE ===")
    print(result_scene.model_dump_json(indent=2))
