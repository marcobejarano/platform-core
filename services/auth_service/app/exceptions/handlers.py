from typing import Any, cast

import structlog
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from services.auth_service.app.exceptions.base import AuthServiceException
from services.auth_service.app.observability.decorators.exception_metrics import (
    record_exception,
)

logger = structlog.get_logger(__name__)


def _get_duration(request: Request) -> float | None:
    return getattr(request.state, "duration_ms", None)


# -------------------------
# Domain exceptions
# -------------------------


async def auth_service_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    exc = cast(AuthServiceException, exc)
    duration = _get_duration(request)

    record_exception(
        exception_type=exc.__class__.__name__,
        status_code=exc.status_code,
        duration_ms=duration,
    )

    logger.warning(
        "auth_service_exception",
        message=exc.message,
        details=exc.details,
        status_code=exc.status_code,
        path=request.url.path,
        method=request.method,
        duration_ms=duration,
    )

    payload: dict[str, Any] = {"detail": exc.message}

    if exc.details:
        payload["details"] = exc.details

    return JSONResponse(
        status_code=exc.status_code,
        content=payload,
    )


# -------------------------
# Validation errors
# -------------------------


async def request_validation_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    exc = cast(RequestValidationError, exc)
    duration = _get_duration(request)

    record_exception(
        exception_type=exc.__class__.__name__,
        status_code=422,
        duration_ms=duration,
    )

    logger.warning(
        "request_validation_error",
        errors=exc.errors(),
        path=request.url.path,
        method=request.method,
        duration_ms=duration,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


# -------------------------
# Database errors
# -------------------------


async def sqlalchemy_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    exc = cast(SQLAlchemyError, exc)
    duration = _get_duration(request)

    record_exception(
        exception_type=exc.__class__.__name__,
        status_code=500,
        duration_ms=duration,
    )

    logger.error(
        "database_error",
        error=str(exc),
        path=request.url.path,
        method=request.method,
        duration_ms=duration,
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database error occurred"},
    )


# -------------------------
# Fallback
# -------------------------


async def generic_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    duration = _get_duration(request)

    record_exception(
        exception_type=exc.__class__.__name__,
        status_code=500,
        duration_ms=duration,
    )

    logger.error(
        "unhandled_exception",
        error=str(exc),
        path=request.url.path,
        method=request.method,
        duration_ms=duration,
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )
