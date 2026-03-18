import os

import structlog
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from observability.logs.logging_config import setup_logging
from observability.logs.structlog_config import setup_structlog
from observability.metrics.metrics_config import setup_metrics
from observability.resource.resource import get_service_resource
from observability.traces.tracing_config import setup_tracing


def setup_observability(
    otlp_endpoint: str | None = None,
    service_name: str | None = None,
    service_namespace: str | None = None,
    service_version: str | None = None,
    deployment_env: str | None = None,
):
    if otlp_endpoint is None:
        otlp_endpoint = os.getenv(
            "OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"
        )

    # Build the service-specific resource
    resource = get_service_resource(
        service_name=service_name,
        service_namespace=service_namespace,
        service_version=service_version,
        deployment_env=deployment_env,
    )

    tracer_provider = setup_tracing(otlp_endpoint, resource)
    meter_provider = setup_metrics(otlp_endpoint, resource)
    logger_provider = setup_logging(otlp_endpoint, resource)
    setup_structlog()

    set_global_textmap(
        CompositePropagator([TraceContextTextMapPropagator(), W3CBaggagePropagator()])
    )

    log = structlog.get_logger(__name__)
    log.info("Observability initialized", endpoint=otlp_endpoint, service=service_name)

    return {
        "tracer_provider": tracer_provider,
        "meter_provider": meter_provider,
        "logger_provider": logger_provider,
    }
