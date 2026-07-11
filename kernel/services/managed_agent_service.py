from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Capability(str, Enum):
    PYTHON = "python"
    NODE = "node"
    TERMINAL = "terminal"
    BROWSER = "browser"
    FILESYSTEM = "filesystem"
    PACKAGE_INSTALL = "package_install"
    SEARCH = "search"
    SCHEDULE = "schedule"
    PARALLEL = "parallel"


CAPABILITY_ALIASES: dict[str, Capability] = {
    "python": Capability.PYTHON,
    "node": Capability.NODE,
    "terminal": Capability.TERMINAL,
    "browser": Capability.BROWSER,
    "fs": Capability.FILESYSTEM,
    "filesystem": Capability.FILESYSTEM,
    "package": Capability.PACKAGE_INSTALL,
    "package_install": Capability.PACKAGE_INSTALL,
    "search": Capability.SEARCH,
    "schedule": Capability.SCHEDULE,
    "parallel": Capability.PARALLEL,
}


class ExecutionRequest(BaseModel):
    capability: str
    mission_id: str
    organization_id: str | None = None
    department_id: str | None = None
    worker_id: str | None = None
    input: dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: int = Field(default=60, gt=0, le=600)
    retries: int = Field(default=0, ge=0, le=5)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def resolved_capability(self) -> Capability:
        canonical = CAPABILITY_ALIASES.get(self.capability.lower())
        if not canonical:
            raise ValueError(f"Unknown capability: {self.capability}")
        return canonical


class ExecutionArtifact(BaseModel):
    type: str
    content_ref: str
    content_hash: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExecutionResult(BaseModel):
    exit_status: int
    logs: str = ""
    artifacts: list[ExecutionArtifact] = Field(default_factory=list)
    mission_graph_node_ref: str | None = None
    emitted_events: list[str] = Field(default_factory=list)
    attempts: int = 1


class TimeoutRetryPolicy(BaseModel):
    default_timeout_seconds: int = 60
    max_retries: int = 2
    backoff_factor: float = 1.5
    retryable_statuses: tuple[int, ...] = (1432, 1433)
