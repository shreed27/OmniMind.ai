from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_observatory_endpoints() -> None:
    # 1. Organization Read Model
    response = client.get("/api/v1/observatory/organizations/org-123")
    assert response.status_code == 200
    assert response.json()["organization_id"] == "org-123"

    # 2. Organization Digital Twin
    response = client.get("/api/v1/observatory/organizations/org-123/twin")
    assert response.status_code == 200
    assert "twin_projection" in response.json()
    assert len(response.json()["topology"]["nodes"]) > 0

    # 3. Department Read Model
    response = client.get("/api/v1/observatory/departments/dep-123")
    assert response.status_code == 200
    assert response.json()["department_id"] == "dep-123"


def test_executive_board_endpoints() -> None:
    # 1. Executive Debate transcript
    response = client.get("/api/v1/executive-board/missions/m-123/debate")
    assert response.status_code == 200
    assert response.json()["status"] in {"completed", "debating"}
    assert len(response.json()["debate_transcript"]) == 3

    # 2. Executive votes listing
    response = client.get("/api/v1/executive-board/missions/m-123/votes")
    assert response.status_code == 200
    assert response.json()["outcome"] == "PASSED"

    # 3. Executive override
    payload = {"decision": "APPROVED", "reason": "Strategic business necessity"}
    response = client.post("/api/v1/executive-board/missions/m-123/override", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "override_applied"


def test_resource_endpoints() -> None:
    # 1. Resource balances
    response = client.get("/api/v1/resources/balances")
    assert response.status_code == 200
    assert "BUDGET" in response.json()["balances"]

    # 2. Transaction ledger history
    response = client.get("/api/v1/resources/history")
    assert response.status_code == 200
    assert len(response.json()) > 0

    # 3. Budget escalation approval
    payload = {"approval_id": "esc-123", "decision": "APPROVED"}
    response = client.post("/api/v1/resources/approve-escalation", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "resolved"


def test_memory_endpoints() -> None:
    # 1. Memory search
    response = client.get("/api/v1/memory/search?query=neural")
    assert response.status_code == 200
    assert len(response.json()) > 0

    # 2. Knowledge graph query
    response = client.get("/api/v1/memory/knowledge?query=neural")
    assert response.status_code == 200
    assert len(response.json()["results"]) > 0
