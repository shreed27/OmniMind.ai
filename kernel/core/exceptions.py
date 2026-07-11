from __future__ import annotations

from typing import Any


class KernelError(Exception):
    code: str = "KERNEL_ERROR"
    status_code: int = 500
    context: dict[str, Any] = {}

    def __init__(self, message: str, *, context: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.context = context or {}


class InvalidTransitionError(KernelError):
    code = "INVALID_TRANSITION"
    status_code = 409


class MissingDependencyError(KernelError):
    code = "MISSING_DEPENDENCY"
    status_code = 500


class KernelBootError(KernelError):
    code = "KERNEL_BOOT_ERROR"
    status_code = 500


class InvalidEventError(KernelError):
    code = "INVALID_EVENT"
    status_code = 422


class InvalidNodeError(KernelError):
    code = "INVALID_NODE"
    status_code = 422


