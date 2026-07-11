from __future__ import annotations

import pytest

from kernel.services.evolution import EvolutionProposal, EvolutionService


@pytest.mark.asyncio
async def test_evolution_propose_emits_and_returns() -> None:
    service = EvolutionService()
    proposal = EvolutionProposal(proposal_id="proposal-1", type="structure", payload={}, confidence=0.8)
    returned = await service.propose(proposal)
    assert returned.proposal_id == "proposal-1"
    assert service.proposals["proposal-1"].type == "structure"
