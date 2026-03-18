from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Auth Service App
    notification_service_name: str = Field(
        default="notification-service",
        description="Unique name of the microservice, used in OpenTelemetry resources",
    )
    notification_service_title: str = Field(
        default="Notification Service", description="Service title"
    )
    notification_service_namespace: str = Field(
        default="backend",
        description="Logical namespace or domain for the service",
    )
    notification_service_version: str = Field(
        default="1.0.0", description="API version"
    )
    notification_service_deployment_env: str = Field(
        default="production",
        description="Deployment environment (e.g. production, staging, dev)",
    )

    # Observability
    otel_exporter_otlp_endpoint: str | None = Field(
        default=None,
        description="OTLP collector endpoint (e.g., http://otel-collector:4317)",
    )

    # Redpanda
    redpanda_bootstrap_servers: str = Field(
        ...,
        description="Comma-separated list of Redpanda bootstrap brokers (e.g. 'localhost:19092,localhost:19093')",
    )
    redpanda_consumer_group: str = Field(
        ...,
        description="Consumer group",
    )

    # Email
    aws_region: str = Field("us-east-1", description="AWS region")
    email_sender: str = Field(
        ...,
        description="Email sender",
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "allow",  # This allows extra env variables without throwing an error
        "case_sensitive": False,
    }


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()  # type: ignore


settings = get_settings()
