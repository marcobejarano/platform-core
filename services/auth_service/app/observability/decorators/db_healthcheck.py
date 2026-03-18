import time
from functools import wraps
from typing import Any, Awaitable, Callable, TypeVar

import structlog
from opentelemetry import trace

from services.auth_service.app.observability.metrics_definitions.auth_service_db_healthcheck_metrics import (
    auth_db_check_counter,
    auth_db_check_duration,
    auth_db_check_errors,
)

tracer = trace.get_tracer("auth-service.db")
logger = structlog.get_logger(__name__)

T = TypeVar("T")


def db_health_check_observed(
    *,
    service: str,
    db: str,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            start = time.perf_counter()

            auth_db_check_counter.add(1, {"service": service, "db": db})

            with tracer.start_as_current_span("auth_db.health_check") as span:
                span.set_attribute("db.system", db)
                span.set_attribute("service.name", service)

                try:
                    return await func(*args, **kwargs)

                except Exception as exc:
                    auth_db_check_errors.add(
                        1,
                        {"service": service, "db": db},
                    )

                    span.record_exception(exc)
                    span.set_status(trace.Status(trace.StatusCode.ERROR))

                    logger.error(
                        "db.connection_failed",
                        service=service,
                        resource=db,
                        error=str(exc),
                        exc_info=True,
                    )
                    raise

                finally:
                    duration_ms = (time.perf_counter() - start) * 1000

                    auth_db_check_duration.record(
                        duration_ms,
                        {"service": service, "db": db},
                    )

                    span.set_attribute("db.latency_ms", duration_ms)

        return wrapper

    return decorator
