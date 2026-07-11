from __future__ import annotations

import pytest
from agents.runtime.python_runtime import PythonRuntime
from agents.runtime.sandbox import Sandbox
from agents.runtime.package_policy import PackagePolicy


def test_python_runtime_executes_code() -> None:
    runtime = PythonRuntime()
    result = runtime.execute("print('ok')")
    assert "ok" in result["stdout"]


def test_sandbox_allows_python() -> None:
    sandbox = Sandbox(policy=PackagePolicy(allowed=["python"]))
    assert sandbox.is_allowed("python") is True
    assert sandbox.is_allowed("browser") is False
