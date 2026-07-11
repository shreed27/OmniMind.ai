from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.exceptions import OmniMindError
from app.main import app

client = TestClient(app)


def test_omni_error_shape() -> None:
    error = OmniMindError("boom", code="BOOM", status_code=400, context={"hint": "nope"})
    assert error.code == "BOOM"
    assert error.context["hint"] == "nope"


def test_health_endpoint_returns_json() -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
