from __future__ import annotations

from typing import Any, Callable, Coroutine

from kernel.core.event import EventEnvelope
from kernel.core.ports import EventBus
from kernel.core.exceptions import InvalidEventError


class InMemoryEventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[[EventEnvelope], Coroutine[Any, Any, None]]]] = {}
        self._dead_letter: list[tuple[str, Exception]] = []

    async def publish(self, event: EventEnvelope) -> str:
        try:
            from kernel.core.event_registry import EventRegistry
            EventRegistry.validate(event)
        except Exception as exc:
            raise InvalidEventError(str(exc)) from exc

        listeners = self._subscribers.get(event.payload.get("name", ""), [])
        for handler in list(listeners):
            try:
                await handler(event)
            except Exception as exc:  # pragma: no cover - defensive
                self._dead_letter.append((event.causal_version, exc))
        return event.causal_version

    def subscribe(
        self,
        event_name: str,
        handler: Callable[[EventEnvelope], Coroutine[Any, Any, None]],
    ) -> str:
        listeners = self._subscribers.setdefault(event_name, [])
        listeners.append(handler)
        return event_name

    async def disconnect(self) -> None:
        self._subscribers.clear()


