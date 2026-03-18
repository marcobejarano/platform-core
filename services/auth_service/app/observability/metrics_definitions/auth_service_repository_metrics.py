from opentelemetry import metrics

meter = metrics.get_meter("auth-service.repository")

# Number of repository calls
repo_calls = meter.create_counter(
    name="repo_calls_total",
    description="Total number of database repository method calls",
)

# Number of errors that occurred inside repository methods
repo_errors = meter.create_counter(
    name="repo_errors_total",
    description="Number of errors that occurred during repository operations",
)

# Execution time for each repository method
repo_latency = meter.create_histogram(
    name="repo_latency_ms",
    description="Duration of database repository operations in milliseconds",
    unit="ms",
)
