import time
from functools import wraps
from typing import Callable, TypeVar

from opentelemetry import trace

from services.auth_service.app.observability.metrics_definitions.auth_service_supabase_metrics import (
    supabase_request_counter,
    supabase_request_duration,
    supabase_request_errors,
)

T = TypeVar("T")

tracer = trace.get_tracer("auth-service.supabase")


def supabase_observed(
    *,
    role: str,
    operation: str,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            start = time.perf_counter()

            with tracer.start_as_current_span(
                f"supabase.{operation}",
                attributes={
                    "supabase.role": role,
                    "supabase.operation": operation,
                },
            ) as span:
                try:
                    result = func(*args, **kwargs)

                    supabase_request_counter.add(
                        1,
                        {"role": role, "operation": operation},
                    )

                    return result

                except Exception as exc:
                    supabase_request_errors.add(
                        1,
                        {"role": role, "operation": operation},
                    )

                    span.record_exception(exc)
                    span.set_status(trace.Status(trace.StatusCode.ERROR))

                    raise

                finally:
                    duration_ms = (time.perf_counter() - start) * 1000

                    supabase_request_duration.record(
                        duration_ms,
                        {"role": role, "operation": operation},
                    )

                    span.set_attribute("supabase.duration_ms", duration_ms)

        return wrapper

    return decorator
