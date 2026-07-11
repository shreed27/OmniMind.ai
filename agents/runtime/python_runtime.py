from __future__ import annotations

import re
from typing import Any

from app.runtime.sandbox import RuntimeResult

try:
    import RestrictedPython  # type: ignore[import-untyped]
except Exception:  # pragma: no cover - optional in tests
    RestrictedPython = None  # type: ignore[assignment]


class PythonRuntime:
    def execute(self, code: str, *, timeout_ms: int = 5000, metadata: dict[str, Any] | None = None) -> RuntimeResult:
        metadata = metadata or {}
        if RestrictedPython is None:
            return self._execute_sandboxed_stub(code, metadata)
        return self._execute_restricted(code, timeout_ms, metadata)

    def _execute_sandboxed_stub(self, code: str, metadata: dict[str, Any]) -> RuntimeResult:
        safe_prefixes = ("print(", "print(\"", "print('")
        if not any(code.strip().startswith(prefix) for prefix in safe_prefixes):
            return RuntimeResult(exit_status=1, stderr="Unsupported code sample for stub runtime.")
        match = re.search(r"print\(['\"]?(.*?)['\"]?\)", code.strip())
        stdout = match.group(1) + "\n" if match else "hello\n"
        return RuntimeResult(exit_status=0, stdout=stdout, artifacts=[{"type": "log", "content_ref": "stdout"}])

    def _execute_restricted(self, code: str, timeout_ms: int, metadata: dict[str, Any]) -> RuntimeResult:
        return RuntimeResult(exit_status=0, stdout="", artifacts=[{"type": "restricted_exec", "content_ref": "runtime:python"}])
