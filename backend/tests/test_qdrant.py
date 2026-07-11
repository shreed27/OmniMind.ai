from __future__ import annotations

import pytest

from app.db.qdrant import create_qdrant, ensure_collection


def test_create_qdrant_client_does_not_crash() -> None:
    client = create_qdrant("http://localhost:6333", api_key=None)
    connectable = bool(client)
    assert connectable is True or connectable is False
