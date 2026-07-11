from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any
from kernel.services.gemini_copilot import GeminiCopilotService

router = APIRouter(prefix="/api/v1/executive-board", tags=["executive-board"])
gemini_service = GeminiCopilotService()


class OverrideRequest(BaseModel):
    decision: str
    reason: str


@router.get("/missions/{id}/debate")
async def get_mission_debate(id: str) -> dict[str, Any]:
    # Custom simulation target based on mission ID or default
    objective = f"Optimize corporate production workflow for {id}"
    result = await gemini_service.generate_debate(objective)
    return {
        "mission_id": id,
        "status": "completed" if result.get("outcome") == "PASSED" else "debating",
        "conflict": result.get("conflict"),
        "debate_transcript": result.get("debate_transcript"),
    }


@router.get("/missions/{id}/votes")
async def get_mission_votes(id: str) -> dict[str, Any]:
    objective = f"Optimize corporate production workflow for {id}"
    result = await gemini_service.generate_debate(objective)
    return {
        "mission_id": id,
        "vote_id": "vote-987",
        "status": "completed",
        "votes": result.get("votes"),
        "outcome": result.get("outcome"),
    }


@router.post("/missions/{id}/override")
async def override_debate(id: str, request: OverrideRequest) -> dict[str, Any]:
    return {
        "mission_id": id,
        "overridden_by": "Human CEO",
        "action": "FORCE_PASS",
        "decision": request.decision,
        "reason": request.reason,
        "timestamp": "2026-07-11T12:05:00Z",
        "status": "override_applied"
    }
