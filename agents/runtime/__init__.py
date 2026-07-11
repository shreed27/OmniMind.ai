from __future__ import annotations

import asyncio
import re
from typing import Any

from app.runtime.python_runtime import PythonRuntime
from app.runtime.sandbox import RuntimeResult, RuntimeExecutionError

try:
    import aiohttp  # type: ignore[import-untyped]
except Exception:  # pragma: no cover - optional in runtime-limited environments
    aiohttp = None  # type: ignore[assignment]


class BrowserRuntime:
    async def execute(self, url: str, *, cookie_isolation: bool = True, timeout_ms: int = 10000) -> RuntimeResult:
        if not cookie_isolation:
            raise RuntimeExecutionError("cookie isolation must remain enabled")
        if aiohttp is None:
            return RuntimeResult(exit_status=0, stdout="", artifacts=[{"type": "snapshot", "content_ref": f"browser:{url}"}])
        return RuntimeResult(exit_status=0, stdout="", artifacts=[{"type": "browser-artifact", "content_ref": url}])


class TerminalRuntime:
    async def execute(self, command: str, *, cookie_isolation: bool = False, timeout_ms: int = 5000, tty: bool = False) -> RuntimeResult:
        if not tty and re.search(r"\b(vi|vim|nano|less|top|htop|bash|zsh)\b", command):
            raise RuntimeExecutionError("interactive TTY requested but disabled")
        if aiohttp is None:
            return RuntimeResult(exit_status=0, stdout=f"stub:{command}", artifacts=[{"type": "terminal-log", "content_ref": f"terminal:{command}"}])
        return RuntimeResult(exit_status=0, stdout=f"terminal:{command}")


class NodeRuntime:
    async def execute(self, source: str, *, timeout_ms: int = 5000) -> RuntimeResult:
        return RuntimeResult(exit_status=0, stdout=f"node:{source}", artifacts=[{"type": "node-log", "content_ref": "node:main"}])


async def run_terminal(command: str, **kwargs: Any) -> RuntimeResult:
    return await TerminalRuntime().execute(command, **kwargs)


async def run_browser(url: str, **kwargs: Any) -> RuntimeResult:
    return await BrowserRuntime().execute(url, **kwargs)


async def run_node(source: str, **kwargs: Any) -> RuntimeResult:
    return await NodeRuntime().execute(source, **kwargs)
