from opentelemetry import metrics

meter = metrics.get_meter("auth-service.router")

router_calls = meter.create_counter(
    name="router_calls_total",
    description="Total router handler calls",
)

router_errors = meter.create_counter(
    name="router_errors_total",
    description="Total router handler errors",
)

router_latency = meter.create_histogram(
    name="router_latency_ms",
    description="Latency of router operations in ms",
    unit="ms",
)
