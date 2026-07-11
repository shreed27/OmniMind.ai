from __future__ import annotations

from typing import Any, Protocol


class EventBusPort(Protocol):
    def publish(self, event: Any) -> None:
        ...

    def subscribe(self, event_name: str, handler: Any) -> None:
        ...
