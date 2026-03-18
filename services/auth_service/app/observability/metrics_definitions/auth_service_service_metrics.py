from opentelemetry import metrics

meter = metrics.get_meter("auth-service.service")

service_calls = meter.create_counter(
    name="service_calls_total",
    description="Number of service-level calls",
)

service_errors = meter.create_counter(
    name="service_errors_total",
    description="Number of failed service-level calls",
)

service_latency = meter.create_histogram(
    name="service_latency_ms",
    description="Latency of service-level operations in milliseconds",
    unit="ms",
)
