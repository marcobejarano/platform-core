from opentelemetry import metrics

# Meter scoped to auth/security concerns
meter = metrics.get_meter("auth-service.dependencies")

auth_dependency_calls = meter.create_counter(
    name="auth_dependency_calls_total",
    description="Total calls to auth-related dependencies",
)

auth_dependency_errors = meter.create_counter(
    name="auth_dependency_errors_total",
    description="Total errors raised by auth-related dependencies",
)

auth_dependency_latency = meter.create_histogram(
    name="auth_dependency_latency_ms",
    description="Latency of auth-related dependencies in milliseconds",
    unit="ms",
)
