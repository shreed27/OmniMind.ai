from __future__ import annotations

import pytest


def test_healthz(client: pytest.FixtureRequest) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_available(client: pytest.FixtureRequest) -> None:
    response = client.get("/api/docs")
    assert response.status_code == 200


def test_root_returns_404(client: pytest.FixtureRequest) -> None:
    response = client.get("/")
    assert response.status_code == 404
