from __future__ import annotations

from typing import Any


class OmniMindError(Exception):
    """Base application error."""

    def __init__(self, message: str, *, code: str = "UNKNOWN_ERROR", status_code: int = 500, context: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.context = context or {}


class StartupError(OmniMindError):
    def __init__(self, message: str, *, context: dict[str, Any] | None = None) -> None:
        super().__init__(message, code="STARTUP_ERROR", status_code=500, context=context)


class ConfigurationError(OmniMindError):
    def __init__(self, message: str, *, context: dict[str, Any] | None = None) -> None:
        super().__init__(message, code="CONFIGURATION_ERROR", status_code=500, context=context)


class NotFoundError(OmniMindError):
    def __init__(self, message: str, *, context: dict[str, Any] | None = None) -> None:
        super().__init__(message, code="NOT_FOUND", status_code=404, context=context)


class ConflictError(OmniMindError):
    def __init__(self, message: str, *, context: dict[str, Any] | None = None) -> None:
        super().__init__(message, code="CONFLICT", status_code=409, context=context)


class ValidationError(OmniMindError):
    def __init__(self, message: str, *, context: dict[str, Any] | None = None) -> None:
        super().__init__(message, code="VALIDATION_ERROR", status_code=422, context=context)
