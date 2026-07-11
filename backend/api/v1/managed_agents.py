from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.managed_agents import execute_managed_agent

router = APIRouter()
router.add_api_route("/execute", execute_managed_agent, methods=["POST"], tags=["managed-agents"])
