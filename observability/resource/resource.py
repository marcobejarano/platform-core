import os
import socket

from opentelemetry.sdk.resources import (
    DEPLOYMENT_ENVIRONMENT,
    SERVICE_INSTANCE_ID,
    SERVICE_NAME,
    SERVICE_NAMESPACE,
    SERVICE_VERSION,
    Resource,
)


def get_service_resource(
    service_name: str | None = None,
    service_namespace: str | None = None,
    service_version: str | None = None,
    deployment_env: str | None = None,
) -> Resource:
    """
    Create and return a custom Resource with service-level attributes.
    Each service can override any of these values.
    """
    service_name = service_name or os.getenv("OTEL_SERVICE_NAME", "default-service")
    service_namespace = service_namespace or os.getenv("OTEL_SERVICE_NAMESPACE", "app")
    service_version = service_version or os.getenv("OTEL_SERVICE_VERSION", "1.0.0")
    deployment_env = deployment_env or os.getenv("DEPLOYMENT_ENVIRONMENT", "production")
    hostname = socket.gethostname()

    return Resource.create(
        {
            SERVICE_NAME: service_name,
            SERVICE_NAMESPACE: service_namespace,
            SERVICE_VERSION: service_version,
            DEPLOYMENT_ENVIRONMENT: deployment_env,
            SERVICE_INSTANCE_ID: hostname,
        }
    )
