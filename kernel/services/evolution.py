from __future__ import annotations

from typing import Any

from app.core.events import emit
from app.core.logging import get_logger
from pydantic import BaseModel

from kernel.services.reflection import ReflectionOutput

logger = get_logger("kernel.services.evolution")


class EvolutionProposal(BaseModel):
    proposal_id: str
    type: str
    payload: dict[str, Any]
    confidence: float = 0.0


class EvolutionService:
    def __init__(self, *, approved: bool = False) -> None:
        self.approved = approved
        self.proposals: dict[str, EvolutionProposal] = {}

    async def propose(self, proposal: EvolutionProposal) -> EvolutionProposal:
        self.proposals[proposal.proposal_id] = proposal
        emit("EvolutionProposed", proposal.model_dump(), {"proposal_id": proposal.proposal_id})
        return proposal

    async def apply(self, proposal_id: str, reflection: ReflectionOutput | None = None) -> None:
        if not self.approved:
            raise PermissionError("Executive approval required before applying evolution")
        proposal = self.proposals[proposal_id]
        emit("EvolutionApplied", {"proposal_id": proposal_id, "type": proposal.type}, {"proposal_id": proposal_id})

    async def revert(self, proposal_id: str) -> None:
        proposal = self.proposals[proposal_id]
        emit("EvolutionReverted", {"proposal_id": proposal_id, "type": proposal.type}, {"proposal_id": proposal_id})


__all__ = ["EvolutionProposal", "EvolutionService"]
