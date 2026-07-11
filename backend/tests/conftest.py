from collections.abc import Generator, AsyncGenerator
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent.parent
for candidate in (ROOT, ROOT / "backend"):
    path = str(candidate)
    if path not in sys.path:
        sys.path.insert(0, path)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
async def async_db_session() -> AsyncGenerator[AsyncSession, None]:
    from app.db.session import init_db, dispose_db, get_session
    await init_db()
    async with get_session() as session:
        yield session
    await dispose_db()

