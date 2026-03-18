from observability.instrumentation.instrumentation import setup_observability
from services.auth_service.app.settings import settings


def init_observability():
    return setup_observability(
        otlp_endpoint=settings.otel_exporter_otlp_endpoint,
        service_name=settings.auth_service_name,
        service_namespace=settings.auth_service_namespace,
        service_version=settings.auth_service_version,
        deployment_env=settings.auth_service_deployment_env,
    )
