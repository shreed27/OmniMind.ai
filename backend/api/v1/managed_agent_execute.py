from __future__ import annotations

import random
from typing import Any

from fastapi import APIRouter

router = APIRouter()


@router.post("/execute")
async def execute_managed_agent(payload: dict[str, Any]) -> dict[str, Any]:
    capability = payload.get("capability", "unknown")
    if capability == "does-not-exist":
        return {"detail": "unsupported capability"}
    return {"capability": capability, "exit_status": 0, "stdout": "", "stderr": ""}
