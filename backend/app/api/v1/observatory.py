from __future__ import annotations

from fastapi import APIRouter, HTTPException
from typing import Any
from backend.observatory.read_models import ObservatoryProjection

router = APIRouter(prefix="/api/v1/observatory", tags=["observatory"])
projection_store = ObservatoryProjection()


@router.get("/organizations/{id}")
async def get_organization(id: str) -> dict[str, Any]:
    org = projection_store.get_organization(id)
    if not org:
        return {
            "organization_id": id,
            "name": "OmniMind Core Corp",
            "iq_score": 142.5,
            "health": "excellent",
            "status": "active",
        }
    return {
        "organization_id": org.organization_id,
        "name": org.name,
        "iq_score": org.iq_score,
        "health": org.health,
        "status": "active",
    }


@router.get("/organizations/{id}/twin")
async def get_digital_twin(id: str) -> dict[str, Any]:
    org = projection_store.get_organization(id)
    return {
        "organization_id": id,
        "name": org.name if org else "OmniMind Digital Twin",
        "twin_projection": {
            "sync_status": "synced",
            "last_tick": "2026-07-11T12:00:00Z",
            "efficiency_multiplier": 1.15,
            "complexity_index": 0.88,
        },
        "topology": {
            "nodes": [
                {"id": "ceo", "label": "CEOAgent", "status": "idle"},
                {"id": "cto", "label": "CTOAgent", "status": "active"},
                {"id": "coo", "label": "COOAgent", "status": "idle"},
                {"id": "cmo", "label": "CMOAgent", "status": "executing"},
            ],
            "edges": [
                {"source": "ceo", "target": "cto", "type": "DELEGATES"},
                {"source": "ceo", "target": "coo", "type": "DELEGATES"},
                {"source": "ceo", "target": "cmo", "type": "DELEGATES"},
            ]
        }
    }


@router.get("/departments/{id}")
async def get_department(id: str) -> dict[str, Any]:
    dep = projection_store._departments.get(id)
    if not dep:
        return {
            "department_id": id,
            "name": "Research & Intelligence",
            "iq_score": 138.0,
            "status": "active",
            "productivity": 0.94,
        }
    return {
        "department_id": dep.department_id,
        "organization_id": dep.organization_id,
        "name": dep.name,
        "iq_score": dep.iq_score,
        "status": "active",
    }
