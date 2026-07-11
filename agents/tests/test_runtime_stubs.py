from __future__ import annotations

from typing import Any

import pytest

from app.runtime.browser_runtime import BrowserRuntime
from app.runtime.node_runtime import NodeRuntime
from app.runtime.terminal_runtime import TerminalRuntime
from app.runtime.package_policy import PackagePolicyError, enforce_package_policy, install_packages, package_policy
from app.runtime.sandbox import RuntimeExecutionError
from app.runtime import runtime as runtime_provider


@pytest.mark.asyncio
async def test_terminal_runtime_disallows_interactive_by_default() -> None:
    with pytest.raises(RuntimeExecutionError):
        await runtime_provider.run_terminal("vim")


@pytest.mark.asyncio
async def test_terminal_runtime_allows_safe_command() -> None:
    result = await runtime_provider.run_terminal("pwd", tty=False)
    assert result.exit_status == 0
    assert result.stdout.startswith("stub:")


@pytest.mark.asyncio
async def test_browser_runtime_requires_cookie_isolation() -> None:
    with pytest.raises(RuntimeExecutionError):
        await BrowserRuntime().execute("https://example.com", cookie_isolation=False)


@pytest.mark.asyncio
async def test_browser_runtime_stub_returns_snapshot_artifact() -> None:
    result = await runtime_provider.run_browser("https://example.com")
    assert result.exit_status == 0
    assert result.artifacts[0]["content_ref"].startswith("browser:")


@pytest.mark.asyncio
async def test_node_runtime_returns_exit_zero() -> None:
    result = await runtime_provider.run_node("console.log(1)")
    assert result.exit_status == 0
    assert result.artifacts == [{"type": "node-log", "content_ref": "node:main"}]


@pytest.mark.asyncio
async def test_node_runtime_supports_custom_timeout() -> None:
    result = await runtime_provider.run_node("console.log(1)", timeout_ms=100)
    assert result.exit_status == 0
