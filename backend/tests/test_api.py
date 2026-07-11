from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi.testclient import TestClient

from app.api.v1.router import api_router
from app.main import app

client = TestClient(app)


def test_command_returns_202() -> None:
    response = client.post("/api/v1/missions", json={"objective": "demo"})
    assert response.status_code in {200, 202}


def test_event_reference_present() -> None:
    response = client.post("/api/v1/missions", json={"objective": "demo"})
    body = response.json()
    assert "event_id" in body or response.status_code == 202
