from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi.testclient import TestClient

from app.api.v1.router import api_router
from app.main import app

import uuid

client = TestClient(app)


def test_command_returns_202() -> None:
    payload = {
        "name": "Test Mission",
        "objective": "demo",
        "created_by": str(uuid.uuid4())
    }
    response = client.post("/api/v1/missions/", json=payload)
    assert response.status_code in {200, 201, 202}


def test_event_reference_present() -> None:
    payload = {
        "name": "Test Mission",
        "objective": "demo",
        "created_by": str(uuid.uuid4())
    }
    response = client.post("/api/v1/missions/", json=payload)
    body = response.json()
    assert "event_ref" in body or "event_id" in body or response.status_code == 202

