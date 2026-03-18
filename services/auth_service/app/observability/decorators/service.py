import time
from functools import wraps
from typing import Any, Awaitable, Callable, TypeVar

import structlog
from opentelemetry import trace

from services.auth_service.app.observability.metrics_definitions.auth_service_service_metrics import (
    service_calls,
    service_errors,
    service_latency,
)

tracer = trace.get_tracer("auth-service.service")
logger = structlog.get_logger(__name__)

T = TypeVar("T")


def service_observed(
    *,
    service: str,
    operation: str,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """
    Service observability decorator:
    - tracing span
    - service-level metrics
    - minimal structured logging
    """

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            start = time.perf_counter()

            service_calls.add(
                1,
                {"service": service, "operation": operation},
            )

            with tracer.start_as_current_span(operation) as span:
                span.set_attribute("service.name", service)
                span.set_attribute("service.operation", operation)

                try:
                    return await func(*args, **kwargs)

                except Exception as exc:
                    service_errors.add(
                        1,
                        {"service": service, "operation": operation},
                    )

                    span.record_exception(exc)
                    span.set_status(trace.Status(trace.StatusCode.ERROR))

                    # Log only once at service boundary
                    logger.error(
                        "service_error",
                        service=service,
                        operation=operation,
                        error_type=type(exc).__name__,
                        error=str(exc),
                        exc_info=True,
                    )

                    raise

                finally:
                    duration_ms = (time.perf_counter() - start) * 1000

                    service_latency.record(
                        duration_ms,
                        {"service": service, "operation": operation},
                    )

                    span.set_attribute("service.latency_ms", duration_ms)

        return wrapper

    return decorator
