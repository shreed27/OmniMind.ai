import pytest
from agents.base import BaseAgent


class DummyAgent(BaseAgent):
    async def execute(self, task: dict[str, object]) -> dict[str, object]:
        return {"status": "ok", **task}


def test_base_agent_execute() -> None:
    agent = DummyAgent()
    result = __import__("asyncio").get_event_loop().run_until_complete(agent.execute({"task_id": "1"}))
    assert result["status"] == "ok"
