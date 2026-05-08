from __future__ import annotations

import json
from typing import Any

from backend.utils.config import get_settings
from backend.utils.client_factory import create_llm_client
from backend.utils.prompt_loader import load_prompt
from backend.schemas import AgentResult, Scene, StoryState, ToolCallRecord, UserAction, WriteSceneArgs
from backend.tools.story import write_scene

settings = get_settings()
MAX_STEPS = 4

AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "write_scene",
            "description": "Escribe o reescribe la siguiente escena del cuento.",
            "parameters": WriteSceneArgs.model_json_schema(),
            "strict": False,
        },
    }
]

def run_agent(state: StoryState, action: UserAction) -> AgentResult:
    return run_agent_loop(state=state, action=action)

def run_agent_loop(
    state: StoryState,
    action: UserAction,
    max_steps: int = MAX_STEPS,
) -> AgentResult:
    
    client = create_llm_client(
        api_key=settings.api_key.get_secret_value(),
        base_url=settings.base_url,
    )

    working_scene: Scene | None = None
    tool_history: list[ToolCallRecord] = []
    repeated_signatures: dict[str, int] = {}

    instructions = load_prompt(
        "run_agent_loop.txt",
        state_json=state.model_dump_json(indent=2),
        user_action_json=action.model_dump_json(indent=2),
    )

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": instructions},
        {
            "role": "user",
            "content": json.dumps(
                {
                    "state": state.model_dump(mode="json"),
                    "action": action.model_dump(mode="json"),
                },
                ensure_ascii=True,
            ),
        },
    ]

    for step in range(1, max_steps + 1):

        response = client.chat.completions.create(
            model=settings.model_name,
            messages=messages,
            tools=AGENT_TOOLS,
            tool_choice="auto",
            parallel_tool_calls=False,
        )

        print(f"\n=== respuesta: {step} ===")
        print(json.dumps(response.model_dump(), ensure_ascii=False, indent=2))
        print("======================\n")

        assistant_message = response.choices[0].message

        print(f"\n=== assistant_message: {step} ===")
        print(json.dumps(assistant_message.model_dump(), ensure_ascii=False, indent=2))
        print("======================\n")

        tool_calls = [
            tool_call
            for tool_call in (assistant_message.tool_calls or [])
            if tool_call.type == "function"
        ]

        print(f"\n=== tool calls: {step} ===")
        print(tool_calls)
        print("======================\n")

        if not tool_calls:
            finish_reason = response.choices[0].finish_reason
            content = assistant_message.content
            raise RuntimeError(
                "Agent loop finished without calling write_scene. "
                f"finish_reason={finish_reason!r}, content={content!r}"
            )

        messages.append(_assistant_message_to_dict(assistant_message))

        print(f"\n=== messages: {step} ===")
        print(json.dumps(message, ensure_ascii=False, indent=2) for message in messages)
        print("======================\n")

        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            signature = _tool_signature(tool_name, arguments)
            repeated_signatures[signature] = repeated_signatures.get(signature, 0) + 1

            print(f"\n=== tool call: {step} ===")
            print(f"tool_name={tool_name}, arguments={arguments}, signature={signature}")
            print("======================\n")

            if repeated_signatures[signature] > 2:
                output_payload = {
                    "error": "repeated_tool_call",
                    "message": "La llamada se esta repitiendo. Debes producir una escena valida.",
                }
            else:
                output_payload = _execute_tool(tool_name=tool_name, arguments=arguments, state=state)

                if tool_name == "write_scene" and "scene" in output_payload:
                    working_scene = Scene.model_validate(output_payload["scene"])

            tool_history.append(
                ToolCallRecord(
                    step=step,
                    tool_name=tool_name,
                    arguments=arguments,
                    output=output_payload,
                )
            )

            print(f"\n=== tool history: {step} ===")
            print(tool_history[-1])
            print("======================\n")

            messages.append(
                _tool_message(tool_call.id, output_payload)
            )

            print(f"\n=== messages: {step} ===")
            print(json.dumps(message, ensure_ascii=False, indent=2) for message in messages)
            print("======================\n")

        if working_scene is not None:
            print(working_scene)
            return AgentResult(
                scene=working_scene,
                reason_summary="Scene generated with the text tool.",
            )

    if working_scene is None:
        raise RuntimeError("Agent loop finished without producing a valid scene.")

    return AgentResult(
        scene=working_scene,
        reason_summary="Fallback result returned after reaching the loop guardrails.",
    )


def _tool_signature(tool_name: str, arguments: dict[str, Any]) -> str:
    return f"{tool_name}:{json.dumps(arguments, sort_keys=True, ensure_ascii=True)}"


def _assistant_message_to_dict(message: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {"role": "assistant"}
    if message.content is not None:
        payload["content"] = message.content
    if message.tool_calls:
        payload["tool_calls"] = [tool_call.model_dump(mode="json") for tool_call in message.tool_calls]
    return payload


def _tool_message(tool_call_id: str, output_payload: dict[str, Any]) -> dict[str, str]:
    return {
        "role": "tool",
        "tool_call_id": tool_call_id,
        "content": json.dumps(output_payload, ensure_ascii=True),
    }


def _execute_tool(
    tool_name: str,
    arguments: dict[str, Any],
    state: StoryState,
) -> dict[str, Any]:
    if tool_name == "write_scene":
        args = WriteSceneArgs.model_validate(arguments)
        scene = write_scene(
            state=state,
            brief=args.brief,
            tone=args.tone,
        )
        return {"scene": scene.model_dump(mode="json")}

    raise ValueError(f"Unknown tool: {tool_name}")

if __name__ == "__main__":

    scene = Scene(
        title="El bosque encantado",
        content="Había una vez un bosque lleno de árboles altos y misteriosos",
    )

    from backend.schemas import StoryState, UserAction, StoryTurn
    turn = StoryTurn(scene=scene)
    state = StoryState(
        story_id="story_123",
        current_scene=turn,
        history=[turn],
        metadata={"author": "Juan"},
    )

    action = UserAction(
        user_message="Escribe la siguiente escena del cuento, donde el protagonista encuentra un objeto mágico.",
    )

    result = run_agent_loop(state=state, action=action)
