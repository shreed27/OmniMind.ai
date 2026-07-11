from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=settings.app_env == "development",
)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


async def init_db() -> None:
    from app.db.base import Base
    from app.db.models.department import Department
    from app.db.models.artifact import Artifact
    from app.db.models.memory import Memory
    from app.db.models.organization import Organization
    from app.db.models.event import Event
    from app.db.models.worker import Worker
    from app.db.models.mission import Mission
    from app.db.models.task import Task

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def dispose_db() -> None:
    await engine.dispose()
