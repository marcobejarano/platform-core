from opentelemetry import metrics

meter = metrics.get_meter("auth-service.exceptions")

# Count how many exceptions occurred
exception_counter = meter.create_counter(
    name="auth_service_exceptions_total",
    description="Total number of handled exceptions in the Auth Service",
)

# Count how many exceptions per HTTP status code
exception_status_counter = meter.create_counter(
    name="auth_service_exception_http_status_total",
    description="Total number of exceptions grouped by HTTP status code",
)

# Duration of failed requests
exception_duration = meter.create_histogram(
    name="auth_service_exception_duration_ms",
    description="Request duration until an exception occurred",
    unit="ms",
)
