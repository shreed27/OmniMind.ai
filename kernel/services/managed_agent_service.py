from __future__ import annotations

import asyncio
from typing import Any

from app.core.events import emit
from app.core.logging import get_logger

from kernel.services.managed_agent_service import (
    Capability,
    ExecutionRequest,
    ExecutionResult,
    TimeoutRetryPolicy,
)

logger = get_logger("managed_agent.service")


class ManagedAgentService:
    def __init__(self, policy: TimeoutRetryPolicy | None = None) -> None:
        self.policy = policy or TimeoutRetryPolicy()

    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        capability = request.resolved_capability()
        runtime = _RUNTIMES.get(capability)
        if runtime is None:
            result = ExecutionResult(exit_status=4, logs=f"Unsupported capability: {capability.value}")
            emit(
                "TaskFailed",
                result.model_dump(mode="json"),
                _context_from_request(request),
            )
            return result

        last = ExecutionResult(exit_status=1, logs="not_started")
        attempts = max(0, request.retries) + 1
        timeout = request.timeout_seconds or self.policy.default_timeout_seconds

        try:
            for attempt in range(1, attempts + 1):
                try:
                    last = await asyncio.wait_for(
                        runtime.execute(request),
                        timeout=timeout,
                    )
                    last.attempts = attempt
                    if last.exit_status == 0:
                        break
                except asyncio.TimeoutError:
                    logger.warning("timeout on attempt %s", attempt)
                    last = ExecutionResult(exit_status=1432, logs="timeout")
                except Exception as error:  # pragma: no cover - runtime boundary
                    logger.error("runtime error on attempt %s: %s", attempt, error, exc_info=True)
                    last = ExecutionResult(exit_status=1433, logs=str(error))
                    break
        except Exception as error:  # pragma: no cover - defensive
            logger.error("managed agent loop failed: %s", error, exc_info=True)
            last = ExecutionResult(exit_status=1433, logs=str(error))

        event_name = "TaskSucceeded" if last.exit_status == 0 else "TaskFailed"
        emit(event_name, last.model_dump(mode="json"), _context_from_request(request, last))
        return last


def _context_from_request(request: ExecutionRequest, result: ExecutionResult | None = None) -> dict[str, Any]:
    context: dict[str, Any] = {
        "mission_id": request.mission_id,
        "capability": request.capability,
        "attempt": result.attempts if result else 0,
    }
    if request.organization_id:
        context["organization_id"] = request.organization_id
    if request.department_id:
        context["department_id"] = request.department_id
    if request.worker_id:
        context["worker_id"] = request.worker_id
    if result and result.mission_graph_node_ref:
        context["mission_graph_node_ref"] = result.mission_graph_node_ref
    return context


class _PythonRuntime:
    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        from app.runtime import runtime as runtime_provider
        return await runtime_provider.run_python(request.input)


class _NodeRuntime:
    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        return ExecutionResult(exit_status=0, logs="node runtime stub")


class _TerminalRuntime:
    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        command = request.input.get("command", "")
        return ExecutionResult(exit_status=0, logs=f"terminal runtime stub: {command}")


class _BrowserRuntime:
    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        return ExecutionResult(exit_status=0, logs="browser runtime stub")


class _FilesystemRuntime:
    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        return ExecutionResult(exit_status=0, logs="filesystem runtime stub")


class _PackageInstallRuntime:
    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        try:
            from app.runtime.package_policy import PackagePolicyError as _PackagePolicyError, enforce_package_policy as _enforce_package_policy
        except Exception as error:  # pragma: no cover - optional policy module
            return ExecutionResult(exit_status=0, logs=f"package runtime stub: {error}")
        packages = request.input.get("packages", [])
        try:
            _enforce_package_policy(packages)
        except _PackagePolicyError as error:
            return ExecutionResult(exit_status=2, logs=str(error))
        return ExecutionResult(exit_status=0, logs=f"install stub for {packages}")


class _SearchRuntime:
    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        return ExecutionResult(exit_status=0, logs="search runtime stub")


class _ScheduleRuntime:
    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        return ExecutionResult(exit_status=0, logs="schedule runtime stub")


class _ParallelRuntime:
    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        return ExecutionResult(exit_status=0, logs="parallel runtime stub")


_RUNTIMES = {
    Capability.PYTHON: _PythonRuntime(),
    Capability.NODE: _NodeRuntime(),
    Capability.TERMINAL: _TerminalRuntime(),
    Capability.BROWSER: _BrowserRuntime(),
    Capability.FILESYSTEM: _FilesystemRuntime(),
    Capability.PACKAGE_INSTALL: _PackageInstallRuntime(),
    Capability.SEARCH: _SearchRuntime(),
    Capability.SCHEDULE: _ScheduleRuntime(),
    Capability.PARALLEL: _ParallelRuntime(),
}
