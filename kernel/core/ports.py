from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine, Protocol, runtime_checkable

from kernel.core.event import EventEnvelope


@runtime_checkable
class EventBus(Protocol):
    async def publish(self, event: EventEnvelope) -> str:
        ...

    def subscribe(self, event_name: str, handler: Callable[[EventEnvelope], Coroutine[Any, Any, None]]) -> str:
        ...

    async def disconnect(self) -> None:
        ...


@runtime_checkable
class MissionGraphStore(Protocol):
    async def append_node(self, node: dict[str, Any]) -> str:
        ...

    async def append_edge(self, edge: dict[str, Any]) -> str:
        ...

    async def query_nodes(self, mission_id: str, limit: int) -> list[dict[str, Any]]:
        ...
