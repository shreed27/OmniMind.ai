from __future__ import annotations

import asyncio
from typing import Any

from app.core.events import emit
from app.core.logging import get_logger
from pydantic import BaseModel

from kernel.services.evolution import EvolutionProposal, EvolutionService
from kernel.services.reflection import ReflectionInput, ReflectionOutput

logger = get_logger("kernel.services.learning")


class LearningOutput(BaseModel):
    mission_dna: dict[str, Any] | None = None
    organization_iq_delta: float = 0.0
    plasticity_delta: float = 0.0


class LearningService:
    def __init__(self, *, reflection_service: Any = None) -> None:
        self.reflection_service = reflection_service

    async def consume(self, payload: ReflectionInput) -> LearningOutput:
        reflection: ReflectionOutput = await self.reflection_service.run(payload)
        output = LearningOutput(mission_dna={"mission_id": payload.mission_id}, organization_iq_delta=0.1, plasticity_delta=0.05)
        evolution_service = EvolutionService()
        await evolution_service.propose(EvolutionProposal(proposal_id=f"learning:{payload.mission_id}", type="org-improvement", payload=output.model_dump(), confidence=0.5))
        emit(
            "LearningCompleted",
            {
                "mission_id": payload.mission_id,
                "mission_dna": output.mission_dna,
                "organization_iq_delta": output.organization_iq_delta,
                "plasticity_delta": output.plasticity_delta,
            },
            {"mission_id": payload.mission_id},
        )
        return output


__all__ = ["LearningOutput", "LearningService"]
