from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, List

router = APIRouter(prefix="/api/v1/resources", tags=["resources"])


class EscalationRequest(BaseModel):
    approval_id: str
    decision: str


@router.get("/balances")
async def get_resource_balances() -> dict[str, Any]:
    return {
        "organization_id": "org-1",
        "balances": {
            "BUDGET": {"amount": 25000.0, "unit": "USD"},
            "GPU_COMPUTE": {"amount": 450.0, "unit": "HOURS"},
            "LLM_TOKENS": {"amount": 125000000.0, "unit": "TOKENS"},
        },
        "allocated": {
            "engineering": {"BUDGET": 12000.0, "GPU_COMPUTE": 300.0},
            "marketing": {"BUDGET": 8000.0, "GPU_COMPUTE": 50.0},
            "operations": {"BUDGET": 5000.0, "GPU_COMPUTE": 100.0}
        }
    }


@router.get("/history")
async def get_ledger_history() -> List[dict[str, Any]]:
    return [
        {
            "ledger_id": "ledger-001",
            "organization_id": "org-1",
            "department_id": "engineering",
            "direction": "credit",
            "amount": 10000.0,
            "resource_type": "BUDGET",
            "balance_after": 10000.0,
            "reason": "initial_capital_allocation",
            "created_at": "2026-07-11T10:00:00Z"
        },
        {
            "ledger_id": "ledger-002",
            "organization_id": "org-1",
            "department_id": "engineering",
            "direction": "debit",
            "amount": 2500.0,
            "resource_type": "BUDGET",
            "balance_after": 7500.0,
            "reason": "gpu_cluster_lease",
            "created_at": "2026-07-11T11:30:00Z"
        }
    ]


@router.post("/approve-escalation")
async def approve_escalation(request: EscalationRequest) -> dict[str, Any]:
    return {
        "approval_id": request.approval_id,
        "decision": request.decision,
        "status": "resolved",
        "applied_by": "CFO",
        "timestamp": "2026-07-11T12:08:00Z"
    }
