from __future__ import annotations


class EvolutionService:
    async def propose(self, mission_id: str) -> dict[str, object]:
        return {"mission_id": mission_id, "proposals": []}
