"""
Error Contract Enforcer - TASK-3.7

Validates that all API errors follow standardized error schema.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.app.core.exceptions import OmniMindError
from backend.app.core.logging import get_logger

logger = get_logger("error_enforcer")


class ErrorResponse(BaseModel):
    """
    Standardized error response schema.

    All API errors must conform to this contract.
    """

    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    status_code: int = Field(..., description="HTTP status code", ge=100, le=599)
    trace_id: str = Field(..., description="Trace ID for debugging")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional error context",
    )
    mission_id: str | None = Field(default=None, description="Associated mission ID")
    organization_id: str | None = Field(
        default=None,
        description="Associated organization ID",
    )
    department_id: str | None = Field(
        default=None,
        description="Associated department ID",
    )
    worker_id: str | None = Field(default=None, description="Associated worker ID")


class ErrorContractEnforcer:
    """
    Enforces error contract compliance across all API responses.

    Ensures every error follows the ErrorResponse schema and logs
    properly for observability.
    """

    @staticmethod
    def create_error_response(
        *,
        code: str,
        message: str,
        status_code: int,
        trace_id: UUID | None = None,
        context: dict[str, Any] | None = None,
        mission_id: str | None = None,
        organization_id: str | None = None,
        department_id: str | None = None,
        worker_id: str | None = None,
    ) -> ErrorResponse:
        """Create standardized error response."""
        return ErrorResponse(
            code=code,
            message=message,
            status_code=status_code,
            trace_id=str(trace_id or uuid4()),
            timestamp=datetime.utcnow().isoformat() + "Z",
            context=context or {},
            mission_id=mission_id,
            organization_id=organization_id,
            department_id=department_id,
            worker_id=worker_id,
        )

    @staticmethod
    def from_omnimind_error(
        error: OmniMindError,
        trace_id: UUID | None = None,
    ) -> ErrorResponse:
        """Convert OmniMindError to standardized error response."""
        return ErrorContractEnforcer.create_error_response(
            code=error.code,
            message=str(error),
            status_code=error.status_code,
            trace_id=trace_id,
            context=error.context,
        )

    @staticmethod
    def from_validation_error(
        error: RequestValidationError,
        trace_id: UUID | None = None,
    ) -> ErrorResponse:
        """Convert Pydantic validation error to standardized response."""
        validation_errors = []
        for err in error.errors():
            validation_errors.append(
                {
                    "field": ".".join(str(loc) for loc in err["loc"]),
                    "message": err["msg"],
                    "type": err["type"],
                },
            )

        return ErrorContractEnforcer.create_error_response(
            code="VALIDATION_ERROR",
            message="Request validation failed",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            trace_id=trace_id,
            context={"validation_errors": validation_errors},
        )

    @staticmethod
    def from_generic_exception(
        error: Exception,
        trace_id: UUID | None = None,
    ) -> ErrorResponse:
        """Convert generic exception to standardized error response."""
        # Log unexpected errors for investigation
        logger.error(
            "Unexpected error occurred: %s",
            str(error),
            exc_info=True,
            extra={"trace_id": str(trace_id or uuid4())},
        )

        return ErrorContractEnforcer.create_error_response(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            trace_id=trace_id,
            context={"error_type": type(error).__name__},
        )


# Exception handlers for FastAPI
async def omnimind_error_handler(
    request: Request,
    exc: OmniMindError,
) -> JSONResponse:
    """Handle OmniMind application errors."""
    trace_id = uuid4()

    error_response = ErrorContractEnforcer.from_omnimind_error(exc, trace_id=trace_id)

    logger.warning(
        "OmniMind error: %s - %s",
        error_response.code,
        error_response.message,
        extra={
            "trace_id": str(trace_id),
            "status_code": error_response.status_code,
            "context": error_response.context,
        },
    )

    return JSONResponse(
        status_code=error_response.status_code,
        content=jsonable_encoder(error_response),
    )


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Handle request validation errors."""
    trace_id = uuid4()

    error_response = ErrorContractEnforcer.from_validation_error(exc, trace_id=trace_id)

    logger.info(
        "Validation error: %s",
        error_response.context.get("validation_errors"),
        extra={"trace_id": str(trace_id)},
    )

    return JSONResponse(
        status_code=error_response.status_code,
        content=jsonable_encoder(error_response),
    )


async def generic_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle unexpected errors."""
    trace_id = uuid4()

    error_response = ErrorContractEnforcer.from_generic_exception(exc, trace_id=trace_id)

    return JSONResponse(
        status_code=error_response.status_code,
        content=jsonable_encoder(error_response),
    )


def register_error_handlers(app: Any) -> None:
    """
    Register error handlers with FastAPI app.

    Must be called during app initialization to enforce error contract.
    """
    app.add_exception_handler(OmniMindError, omnimind_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, generic_error_handler)

    logger.info("Error contract enforcer registered")
