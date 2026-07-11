from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

from app.main import app


def test_execute_supported_capability(client: TestClient) -> None:
    response = client.post(
        "/api/v1/managed-agents/execute",
        json={
            "capability": "python",
            "mission_id": "11111111-1111-1111-1111-111111111111",
            "input": {"code": "print('hello')"},
            "timeout_seconds": 10,
            "retries": 0,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["capability"] == "python"
    assert "exit_status" in body


def test_execute_unsupported_capability(client: TestClient) -> None:
    response = client.post(
        "/api/v1/managed-agents/execute",
        json={
            "capability": "does-not-exist",
            "mission_id": "11111111-1111-1111-1111-111111111111",
        },
    )
    assert response.status_code == 422


def test_execute_with_organization_context(client: TestClient) -> None:
    response = client.post(
        "/api/v1/managed-agents/execute",
        json={
            "capability": "terminal",
            "mission_id": "11111111-1111-1111-1111-111111111111",
            "organization_id": "22222222-2222-2222-2222-222222222222",
            "department_id": "33333333-3333-3333-3333-333333333333",
            "worker_id": "44444444-4444-4444-4444-444444444444",
            "input": {"command": "pwd"},
        },
    )
    assert response.status_code == 200
