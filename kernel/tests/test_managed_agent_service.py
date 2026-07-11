from __future__ import annotations

from typing import Any

import pytest

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_managed_agent_route_registered() -> None:
    response = client.get("/api/v1/managed-agents/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_managed_agent_execute_returns_payload() -> None:
    response = client.post(
        "/api/v1/managed-agents/execute",
        json={
            "capability": "terminal",
            "mission_id": "11111111-1111-1111-1111-111111111111",
            "input": {"command": "pwd"},
            "timeout_seconds": 10,
        },
    )
    assert response.status_code == 200
    assert response.json()["capability"] == "terminal"
