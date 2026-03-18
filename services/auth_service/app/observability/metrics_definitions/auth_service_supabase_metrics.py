from opentelemetry import metrics

meter = metrics.get_meter("auth-service.supabase")

supabase_request_counter = meter.create_counter(
    name="supabase_requests_total",
    description="Number of Supabase requests made",
)

supabase_request_errors = meter.create_counter(
    name="supabase_request_errors_total",
    description="Number of failed Supabase requests",
)

supabase_request_duration = meter.create_histogram(
    name="supabase_request_duration_ms",
    description="Supabase request duration in milliseconds",
    unit="ms",
)
