from services.auth_service.app.observability.metrics_definitions.auth_service_exception_metrics import (
    exception_counter,
    exception_duration,
    exception_status_counter,
)


def record_exception(
    *,
    exception_type: str,
    status_code: int,
    duration_ms: float | None,
) -> None:
    attributes = {
        "exception_type": exception_type,
        "status_code": status_code,
    }

    exception_counter.add(1, attributes)
    exception_status_counter.add(1, attributes)

    if duration_ms is not None:
        exception_duration.record(duration_ms, attributes)
