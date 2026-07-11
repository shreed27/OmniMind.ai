from __future__ import annotations

import pytest

from app.runtime.python_runtime import PythonRuntime
from app.runtime.sandbox import RuntimeResult, RuntimeExecutionError


@pytest.fixture()
def runtime() -> PythonRuntime:
    return PythonRuntime()


@pytest.mark.asyncio
async def test_stub_python_runtime_accepts_print(runtime: PythonRuntime) -> None:
    result = await runtime.execute("print('hello')")
    assert result.exit_status == 0
    assert result.stdout == "hello\n"


@pytest.mark.asyncio
async def test_stub_python_runtime_rejects_complex_code(runtime: PythonRuntime) -> None:
    result = await runtime.execute("import os\nos.system('ls')")
    assert result.exit_status == 1


@pytest.mark.asyncio
async def test_artifact_attached_on_execution(runtime: PythonRuntime) -> None:
    result = await runtime.execute("print('ok')")
    assert any(artifact.get("type") == "log" for artifact in result.artifacts)
