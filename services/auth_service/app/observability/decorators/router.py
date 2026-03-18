import time
from functools import wraps
from typing import Any, Awaitable, Callable, TypeVar

import structlog
from opentelemetry import trace

from services.auth_service.app.observability.metrics_definitions.auth_service_router_metrics import (
    router_calls,
    router_errors,
    router_latency,
)

tracer = trace.get_tracer("auth-service.router")
logger = structlog.get_logger(__name__)

T = TypeVar("T")


def router_observed(
    *,
    route: str,
    method: str,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """
    Router observability decorator:
    - top-level HTTP span
    - router metrics
    - minimal logging (unexpected errors only)
    """

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            start = time.perf_counter()

            router_calls.add(
                1,
                {"route": route, "method": method},
            )

            with tracer.start_as_current_span(f"{method} {route}") as span:
                span.set_attribute("http.route", route)
                span.set_attribute("http.method", method)

                try:
                    return await func(*args, **kwargs)

                except Exception as exc:
                    router_errors.add(
                        1,
                        {"route": route, "method": method},
                    )

                    span.record_exception(exc)
                    span.set_status(trace.Status(trace.StatusCode.ERROR))

                    # Router logs only unexpected failures
                    logger.error(
                        "router_unhandled_error",
                        route=route,
                        method=method,
                        error_type=type(exc).__name__,
                        error=str(exc),
                        exc_info=True,
                    )
                    raise

                finally:
                    duration_ms = (time.perf_counter() - start) * 1000

                    router_latency.record(
                        duration_ms,
                        {"route": route, "method": method},
                    )

                    span.set_attribute("http.latency_ms", duration_ms)

        return wrapper

    return decorator
