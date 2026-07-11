from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.missions import router as missions_router
from app.api.v1.managed_agents import router as managed_agents_router

api_router = APIRouter()
api_router.include_router(missions_router, prefix="/missions", tags=["missions"])
api_router.include_router(managed_agents_router, prefix="/managed-agents", tags=["managed-agents"])
