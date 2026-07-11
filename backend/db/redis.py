from __future__ import annotations

import asyncio
from typing import Any

import redis.asyncio as redis
from redis.asyncio import Redis


def create_redis(url: str) -> Redis:
    return redis.from_url(url, decode_responses=True, socket_connect_timeout=5, socket_keepalive=True)


async def ping(redis_client: Redis) -> bool:
    try:
        return bool(await redis_client.ping())
    except Exception:
        return False
