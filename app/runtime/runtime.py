from __future__ import annotations

from typing import Any
from agents.runtime import (
    run_terminal as run_terminal,
    run_browser as run_browser,
    run_node as run_node,
)
from app.runtime.sandbox import RuntimeResult

async def run_python(payload: dict[str, Any]) -> RuntimeResult:
    from agents.runtime.python_runtime import PythonRuntime
    code = payload.get("code", "")
    timeout_ms = payload.get("timeout_seconds", 5) * 1000
    res = PythonRuntime().execute(code, timeout_ms=timeout_ms)
    return RuntimeResult(
        exit_status=res.exit_status,
        stdout=res.stdout,
        stderr=res.stderr,
        artifacts=res.artifacts,
        duration_ms=res.duration_ms,
    )
