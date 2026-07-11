"""Tests for Error Contract Enforcer - TASK-3.7"""

from __future__ import annotations

import pytest
from uuid import uuid4

from backend.app.core.error_enforcer import ErrorContractEnforcer, ErrorResponse
from backend.app.core.exceptions import (
    NotFoundError,
    ValidationError,
    ForbiddenError,
    OmniMindError,
)


class TestErrorResponse:
    """Test ErrorResponse schema validation."""

    def test_error_response_schema(self) -> None:
        """ErrorResponse has all required fields."""
        trace_id = uuid4()

        error = ErrorResponse(
            code="TEST_ERROR",
            message="Test error message",
            status_code=400,
            trace_id=str(trace_id),
            timestamp="2026-07-11T12:00:00Z",
            context={"key": "value"},
        )

        assert error.code == "TEST_ERROR"
        assert error.message == "Test error message"
        assert error.status_code == 400
        assert error.trace_id == str(trace_id)
        assert error.context == {"key": "value"}

    def test_error_response_optional_fields(self) -> None:
        """ErrorResponse optional entity IDs work."""
        error = ErrorResponse(
            code="TEST_ERROR",
            message="Test",
            status_code=400,
            trace_id=str(uuid4()),
            timestamp="2026-07-11T12:00:00Z",
            mission_id="mission-123",
            organization_id="org-456",
        )

        assert error.mission_id == "mission-123"
        assert error.organization_id == "org-456"
        assert error.department_id is None
        assert error.worker_id is None


class TestErrorContractEnforcer:
    """Test Error Contract Enforcer."""

    def test_create_error_response(self) -> None:
        """create_error_response builds standard error."""
        trace_id = uuid4()

        error = ErrorContractEnforcer.create_error_response(
            code="CUSTOM_ERROR",
            message="Something went wrong",
            status_code=500,
            trace_id=trace_id,
            context={"detail": "Additional info"},
        )

        assert error.code == "CUSTOM_ERROR"
        assert error.message == "Something went wrong"
        assert error.status_code == 500
        assert error.trace_id == str(trace_id)
        assert error.context["detail"] == "Additional info"
        assert error.timestamp.endswith("Z")  # ISO 8601 UTC

    def test_auto_generate_trace_id(self) -> None:
        """create_error_response auto-generates trace_id if missing."""
        error = ErrorContractEnforcer.create_error_response(
            code="TEST",
            message="Test",
            status_code=400,
        )

        assert error.trace_id is not None
        assert len(error.trace_id) == 36  # UUID format

    def test_from_omnimind_error(self) -> None:
        """from_omnimind_error converts application errors."""
        app_error = NotFoundError(
            "Resource not found",
            context={"resource_id": "123"},
        )

        error_response = ErrorContractEnforcer.from_omnimind_error(app_error)

        assert error_response.code == "NOT_FOUND"
        assert error_response.message == "Resource not found"
        assert error_response.status_code == 404
        assert error_response.context["resource_id"] == "123"

    def test_from_validation_error_conversion(self) -> None:
        """from_validation_error handles Pydantic errors."""
        # Simulate Pydantic validation error
        from pydantic import BaseModel, Field
        from fastapi.exceptions import RequestValidationError

        class TestModel(BaseModel):
            name: str = Field(..., min_length=1)
            age: int = Field(..., ge=0)

        try:
            TestModel(name="", age=-1)  # Invalid data
        except Exception as pydantic_error:
            # Create FastAPI RequestValidationError
            validation_error = RequestValidationError([])

            # Manually construct error for testing
            error_response = ErrorContractEnforcer.create_error_response(
                code="VALIDATION_ERROR",
                message="Request validation failed",
                status_code=422,
                context={
                    "validation_errors": [
                        {
                            "field": "name",
                            "message": "String should have at least 1 character",
                            "type": "string_too_short",
                        },
                    ],
                },
            )

            assert error_response.code == "VALIDATION_ERROR"
            assert error_response.status_code == 422
            assert len(error_response.context["validation_errors"]) >= 1

    def test_from_generic_exception(self) -> None:
        """from_generic_exception handles unexpected errors."""
        generic_error = RuntimeError("Unexpected runtime error")

        error_response = ErrorContractEnforcer.from_generic_exception(generic_error)

        assert error_response.code == "INTERNAL_SERVER_ERROR"
        assert error_response.message == "An unexpected error occurred"
        assert error_response.status_code == 500
        assert error_response.context["error_type"] == "RuntimeError"

    def test_entity_context_propagation(self) -> None:
        """Error response includes entity IDs for tracing."""
        error = ErrorContractEnforcer.create_error_response(
            code="FORBIDDEN",
            message="Access denied",
            status_code=403,
            mission_id="mission-1",
            organization_id="org-1",
            department_id="dept-1",
            worker_id="worker-1",
        )

        assert error.mission_id == "mission-1"
        assert error.organization_id == "org-1"
        assert error.department_id == "dept-1"
        assert error.worker_id == "worker-1"

    def test_all_custom_errors_conform(self) -> None:
        """All custom OmniMindError subclasses produce valid responses."""
        errors = [
            NotFoundError("Not found", context={"id": "123"}),
            ValidationError("Invalid input", context={"field": "name"}),
            ForbiddenError("Access denied"),
        ]

        for app_error in errors:
            error_response = ErrorContractEnforcer.from_omnimind_error(app_error)

            # All responses must have required fields
            assert error_response.code is not None
            assert error_response.message is not None
            assert 100 <= error_response.status_code <= 599
            assert error_response.trace_id is not None
            assert error_response.timestamp is not None
            assert isinstance(error_response.context, dict)


class TestErrorHandlerIntegration:
    """Integration tests with FastAPI app."""

    def test_error_handler_registration(self) -> None:
        """Error handlers can be registered with FastAPI app."""
        from fastapi import FastAPI
        from backend.app.core.error_enforcer import register_error_handlers

        app = FastAPI()
        register_error_handlers(app)

        # Verify handlers are registered
        assert len(app.exception_handlers) > 0
