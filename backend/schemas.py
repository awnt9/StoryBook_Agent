from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Scene(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    content: str


class StoryTurn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scene: Scene


class StoryState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    story_id: str | None = None
    current_scene: StoryTurn | None = None
    history: list[StoryTurn] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class UserAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_message: str | None = None


class AgentResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scene: Scene
    reason_summary: str | None = None


class ToolCallRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step: int
    tool_name: str
    arguments: dict[str, Any]
    output: dict[str, Any]


class WriteSceneArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    brief: str
    tone: str | None = None
