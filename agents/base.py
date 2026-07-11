from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator

from events.store import publish_event
from kernel.core.events import EventEnvelope


class AgentProperties(BaseModel):
    agent_id: UUID = Field(default_factory=uuid4)
    name: str = Field(min_length=1)
    role: str = Field(min_length=1)
    department: str | None = None
    mission_id: UUID | None = None
    manager_id: UUID | None = None
    status: str = "sleeping"

    model_config = {"frozen": False}


class BaseAgent:
    def __init__(self, properties: AgentProperties) -> None:
        self.properties = properties

    async def emit(self, name: str, payload: dict[str, Any]) -> EventEnvelope:
        context = {
            "mission_id": str(self.properties.mission_id) if self.properties.mission_id else None,
            "worker_id": str(self.properties.agent_id),
            "department_id": self.properties.department,
            "app": "omnimind",
        }
        return await publish_event(name, payload, {k: v for k, v in context.items() if v})

    def set_status(self, status: str) -> None:
        self.properties.status = status
