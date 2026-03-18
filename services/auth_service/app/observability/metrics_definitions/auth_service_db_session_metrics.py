from opentelemetry import metrics

meter = metrics.get_meter("auth-service.db")

# -------------------------------------------------
# Session lifecycle counters
# -------------------------------------------------

auth_db_session_opened = meter.create_counter(
    name="auth_db_sessions_opened_total",
    description="Number of database sessions opened",
)

auth_db_session_errors = meter.create_counter(
    name="auth_db_session_errors_total",
    description="Number of database sessions that failed",
)

# -------------------------------------------------
# Session duration
# -------------------------------------------------

auth_db_session_duration = meter.create_histogram(
    name="auth_db_session_duration_ms",
    description="Duration of database sessions in milliseconds",
    unit="ms",
)
