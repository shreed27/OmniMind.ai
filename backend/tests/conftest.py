from collections.abc import Generator
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent.parent
for candidate in (ROOT, ROOT / "backend"):
    path = str(candidate)
    if path not in sys.path:
        sys.path.insert(0, path)

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client
