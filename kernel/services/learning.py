from __future__ import annotations


class LearningService:
    async def improve(self, mission_id: str) -> dict[str, object]:
        return {"mission_id": mission_id, "status": "improved"}
