from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


def test_healthz_endpoint(client: TestClient) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
