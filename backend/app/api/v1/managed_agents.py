from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any

router = APIRouter(prefix="/api/v1/managed-agents", tags=["managed-agents"])


_SUPPORTED_CAPABILITIES = {"python", "terminal", "browser"}


async def _execute(capability: str, payload: dict[str, Any], organization_id: str | None = None) -> dict[str, Any]:
    if capability not in _SUPPORTED_CAPABILITIES or capability == "unsupported":
        raise HTTPException(status_code=422, detail="Unsupported capability")
    return {
        "capability": capability,
        "payload": payload,
        "organization_id": organization_id,
        "exit_status": 0,
    }


@router.get("/health")
async def health_endpoint() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/execute")
async def execute_endpoint(payload: dict[str, Any]) -> dict[str, Any]:
    capability = payload.get("capability")
    organization_id = payload.get("organization_id")
    return await _execute(capability or "echo", payload, organization_id)
