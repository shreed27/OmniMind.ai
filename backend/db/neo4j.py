from __future__ import annotations


from neo4j import AsyncGraphDatabase

from app.core.config import get_settings

settings = get_settings()

_driver: AsyncGraphDatabase | None = None


async def get_neo4j_driver() -> AsyncGraphDatabase:
    global _driver
    if _driver is None:
        _driver = AsyncGraphDatabase.driver(
            settings.neo4j_url,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
    return _driver


async def close_neo4j_driver() -> None:
    global _driver
    if _driver is not None:
        await _driver.close()
        _driver = None
