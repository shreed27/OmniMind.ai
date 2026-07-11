from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/healthz")
async def api_healthz() -> dict[str, str]:
    return {"status": "ok"}
