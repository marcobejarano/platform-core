from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from services.auth_service.app.exceptions.base import AuthServiceException
from services.auth_service.app.exceptions.handlers import (
    auth_service_exception_handler,
    generic_exception_handler,
    request_validation_exception_handler,
    sqlalchemy_exception_handler,
)


def setup_exception_handling(app: FastAPI) -> None:
    """
    Register all application-level exception handlers.

    This function should be called once during app initialization
    (e.g., in main.py).
    """

    # -------------------------
    # Domain / service errors
    # -------------------------
    app.add_exception_handler(
        AuthServiceException,
        auth_service_exception_handler,
    )

    # -------------------------
    # Request validation errors
    # -------------------------
    app.add_exception_handler(
        RequestValidationError,
        request_validation_exception_handler,
    )

    # -------------------------
    # Database errors
    # -------------------------
    app.add_exception_handler(
        SQLAlchemyError,
        sqlalchemy_exception_handler,
    )

    # -------------------------
    # Fallback (catch-all)
    # -------------------------
    app.add_exception_handler(
        Exception,
        generic_exception_handler,
    )
