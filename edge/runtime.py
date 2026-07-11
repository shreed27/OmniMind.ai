from __future__ import annotations

from typing import Any


class GemmaEdgeRuntime:
    def __init__(self) -> None:
        self._running = False

    async def start(self) -> None:
        self._running = True

    async def stop(self) -> None:
        self._running = False
