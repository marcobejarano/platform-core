import time
from functools import wraps
from typing import AsyncGenerator, Callable, TypeVar

import structlog
from opentelemetry import trace

from services.auth_service.app.observability.metrics_definitions.auth_service_db_session_metrics import (
    auth_db_session_duration,
    auth_db_session_errors,
    auth_db_session_opened,
)

tracer = trace.get_tracer("auth-service.db")
logger = structlog.get_logger(__name__)

T = TypeVar("T")


def db_session_observed(
    *,
    service: str,
    db: str,
) -> Callable[
    [Callable[..., AsyncGenerator[T, None]]],
    Callable[..., AsyncGenerator[T, None]],
]:
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.perf_counter()

            # -------------------------
            # Metrics: session opened
            # -------------------------
            auth_db_session_opened.add(
                1,
                {"service": service, "db": db},
            )

            with tracer.start_as_current_span("db.session") as span:
                span.set_attribute("service.name", service)
                span.set_attribute("db.name", db)

                try:
                    async for value in func(*args, **kwargs):
                        yield value

                except Exception as exc:
                    # -------------------------
                    # Metrics: session error
                    # -------------------------
                    auth_db_session_errors.add(
                        1,
                        {"service": service, "db": db},
                    )

                    span.record_exception(exc)
                    span.set_status(trace.Status(trace.StatusCode.ERROR))

                    logger.error(
                        "db.session_error",
                        service=service,
                        resource=db,
                        error=str(exc),
                        exc_info=True,
                    )
                    raise

                finally:
                    duration_ms = (time.perf_counter() - start) * 1000

                    # -------------------------
                    # Metrics: session duration
                    # -------------------------
                    auth_db_session_duration.record(
                        duration_ms,
                        {"service": service, "db": db},
                    )

                    span.set_attribute("db.session_duration_ms", duration_ms)

        return wrapper

    return decorator
