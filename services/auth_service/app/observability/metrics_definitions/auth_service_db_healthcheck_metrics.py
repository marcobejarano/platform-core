from opentelemetry import metrics

meter = metrics.get_meter("auth-service.db")

auth_db_check_counter = meter.create_counter(
    name="auth_db_health_checks_total",
    description="Number of DB health checks performed",
)

auth_db_check_errors = meter.create_counter(
    name="auth_db_health_check_errors_total",
    description="Number of failed DB health checks",
)

auth_db_check_duration = meter.create_histogram(
    name="auth_db_health_check_duration_ms",
    description="Duration of DB health checks in milliseconds",
    unit="ms",
)
