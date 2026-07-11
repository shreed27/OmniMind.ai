from __future__ import annotations

from typing import Any, Callable, Coroutine

from kernel.core.event import EventEnvelope
from kernel.core.ports import EventBus


class InMemoryEventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[[EventEnvelope], Coroutine[Any, Any, None]]]] = {}
        self._dead_letter: list[tuple[str, Exception]] = []
        self._history: list[EventEnvelope] = []

    def publish(self, event: EventEnvelope) -> str:
        from kernel.core.event_registry import EventRegistry
        EventRegistry.validate(event)

        listeners = list(self._subscribers.get(event.payload.get("name", "unknown"), []))
        for handler in listeners:
            try:
                handler(event)
            except Exception as exc:  # pragma: no cover - defensive
                self._dead_letter.append((event.causal_version, exc))

        self._history.append(event)
        return event.causal_version

    def subscribe(self, event_name: str, handler: Callable[[EventEnvelope], Coroutine[Any, Any, None]]) -> str:
        listeners = self._subscribers.setdefault(event_name, [])
        listeners.append(handler)
        return event_name

    async def disconnect(self) -> None:
        self._subscribers.clear()

    def history(self) -> list[EventEnvelope]:
        return list(self._history)
