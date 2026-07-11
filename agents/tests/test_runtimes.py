import pytest
from agents.runtime.server_runtime import ServerRuntime, TerminalRuntime


def test_terminal_runtime_executes_command() -> None:
    runtime = TerminalRuntime()
    result = runtime.run("echo hello", timeout=5)
    assert result["returncode"] == 0
    assert "hello" in result["stdout"]


def test_server_runtime_health_reports_url() -> None:
    runtime = ServerRuntime("http://localhost:8000")
    assert runtime.health()["url"] == "http://localhost:8000"
