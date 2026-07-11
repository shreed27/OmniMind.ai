from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class EvolutionProposal:
    proposal_id: str
    type: str
    payload: dict[str, Any]
    confidence: float


class EvolutionService:
    def __init__(self) -> None:
        self.proposals: dict[str, EvolutionProposal] = {}

    async def propose(self, proposal: EvolutionProposal) -> EvolutionProposal:
        self.proposals[proposal.proposal_id] = proposal
        return proposal
