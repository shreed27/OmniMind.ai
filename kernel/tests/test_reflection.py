from __future__ import annotations

import pytest

from kernel.services.reflection import ReflectionInput, ReflectionOutput, ReflectionService


@pytest.mark.asyncio
async def test_reflection_returns_output() -> None:
    service = ReflectionService()
    payload = ReflectionInput(mission_id="mission-1", result={"status": "ok"})
    output: ReflectionOutput = await service.run(payload)
    assert output.lessons
    assert output.knowledge
    assert output.skills
    assert output.recommendations
    assert 0.0 <= output.confidence <= 1.0
