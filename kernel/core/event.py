from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EventEnvelope:
    name: str
    payload: dict[str, Any]
    context: dict[str, Any] = field(default_factory=dict)

    def emit(self) -> None:
        raise NotImplementedError


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[Any]] = {}

    def subscribe(self, event_name: str, handler: Any) -> None:
        self._subscribers.setdefault(event_name, []).append(handler)

    def publish(self, event: EventEnvelope) -> None:
        for handler in self._subscribers.get(event.name, []):
            handler(event)
