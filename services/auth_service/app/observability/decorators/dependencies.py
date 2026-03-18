import time
from functools import wraps
from typing import Any, Awaitable, Callable, TypeVar

import structlog
from opentelemetry import trace

from services.auth_service.app.observability.metrics_definitions.auth_service_dependencies_metrics import (
    auth_dependency_calls,
    auth_dependency_errors,
    auth_dependency_latency,
)

tracer = trace.get_tracer("auth-service.dependencies")
logger = structlog.get_logger(__name__)

T = TypeVar("T")


def observed_dependency(
    operation: str,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """
    Dependency observability decorator:
    - tracing span
    - dependency-level metrics
    - minimal structured logging
    """

    def decorator(
        func: Callable[..., Awaitable[T]],
    ) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            start = time.perf_counter()
            auth_dependency_calls.add(1, {"operation": operation})

            with tracer.start_as_current_span(operation) as span:
                try:
                    return await func(*args, **kwargs)

                except Exception as exc:
                    auth_dependency_errors.add(1, {"operation": operation})

                    span.record_exception(exc)
                    span.set_status(trace.Status(trace.StatusCode.ERROR))

                    logger.warning(
                        "auth_dependency_error",
                        operation=operation,
                        error=str(exc),
                        error_type=type(exc).__name__,
                    )
                    raise

                finally:
                    latency_ms = (time.perf_counter() - start) * 1000
                    auth_dependency_latency.record(
                        latency_ms,
                        {"operation": operation},
                    )
                    span.set_attribute("latency_ms", latency_ms)

        return wrapper

    return decorator
