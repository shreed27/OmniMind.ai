from __future__ import annotations

from typing import Any

from fastapi import FastAPI

from app.runtime.python_runtime import RuntimeResult
from app.runtime.runtime import ManagedAgentService, ExecutionRequest, TimeoutRetryPolicy

managed_agent_service = ManagedAgentService()


def register_managed_agent_routes(application: FastAPI) -> None:
    @application.post("/api/v1/managed-agents/execute", response_model=dict[str, Any])
    async def execute_managed_agent(request: ExecutionRequest) -> dict[str, Any]:
        result = await managed_agent_service.execute(request)
        payload: dict[str, Any] = {
            "capability": request.capability,
            "exit_status": result.exit_status,
            "logs": result.logs,
            "artifacts": [artifact.model_dump() for artifact in result.artifacts],
            "mission_graph_node_ref": result.mission_graph_node_ref,
            "emitted_events": result.emitted_events,
            "attempts": result.attempts,
        }
        if result.mission_graph_node_ref:
            payload["mission_graph_node_ref"] = result.mission_graph_node_ref
        return payload

    @application.get("/api/v1/managed-agents/health")
    async def managed_agent_health() -> dict[str, str]:
        return {"status": "ok"}
