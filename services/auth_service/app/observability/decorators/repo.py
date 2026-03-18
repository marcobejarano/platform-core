import time
from functools import wraps
from typing import Any, Awaitable, Callable, TypeVar

import structlog
from opentelemetry import trace
from sqlalchemy.exc import SQLAlchemyError

from services.auth_service.app.observability.metrics_definitions.auth_service_repository_metrics import (
    repo_calls,
    repo_errors,
    repo_latency,
)

tracer = trace.get_tracer("auth-service.repository.profile")
logger = structlog.get_logger(__name__)

T = TypeVar("T")


def repo_observed(
    operation: str,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """
    Repository observability decorator:
    - tracing span
    - metrics (calls, errors, latency)
    - minimal structured logging
    """

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            start = time.perf_counter()
            repo_calls.add(1, {"operation": operation})

            with tracer.start_as_current_span(operation) as span:
                span.set_attribute("repo.operation", operation)
                span.set_attribute("db.system", "postgresql")

                try:
                    return await func(*args, **kwargs)

                except SQLAlchemyError as sql_exc:
                    # Expected DB error → metric + span status, no noisy logs
                    repo_errors.add(1, {"operation": operation})
                    span.record_exception(sql_exc)
                    span.set_status(trace.Status(trace.StatusCode.ERROR))
                    raise

                except Exception as exc:
                    # Unexpected error → metric + structured log
                    repo_errors.add(1, {"operation": operation})

                    logger.error(
                        "repository_unexpected_error",
                        operation=operation,
                        error_type=type(exc).__name__,
                        error=str(exc),
                        exc_info=True,
                    )

                    span.record_exception(exc)
                    span.set_status(trace.Status(trace.StatusCode.ERROR))
                    raise

                finally:
                    duration_ms = (time.perf_counter() - start) * 1000
                    repo_latency.record(duration_ms, {"operation": operation})
                    span.set_attribute("repo.latency_ms", duration_ms)

        return wrapper

    return decorator
