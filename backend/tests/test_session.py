from __future__ import annotations


import pytest
from sqlalchemy import text

from app.db.session import dispose_db, get_session, init_db


@pytest.mark.asyncio
async def test_db_connection_and_query() -> None:
    await init_db()
    async with get_session() as session:
        result = await session.execute(text("SELECT 1"))
        assert result.scalar_one() == 1
    await dispose_db()


@pytest.mark.asyncio
async def test_db_reconnection_after_pool_dispose() -> None:
    await dispose_db()
    await init_db()
    async with get_session() as session:
        result = await session.execute(text("SELECT current_database()"))
        database = result.scalar_one()
    assert isinstance(database, str)


@pytest.mark.skip(reason="requires running Postgres from docker-compose")
@pytest.mark.asyncio
async def test_db_live_against_docker() -> None:
    await init_db()
    async with get_session() as session:
        result = await session.execute(text("SELECT 1"))
        assert result.scalar_one() == 1
    await dispose_db()
