from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Auth Service App
    auth_service_name: str = Field(
        default="auth-service",
        description="Unique name of the microservice, used in OpenTelemetry resources",
    )
    auth_service_title: str = Field(
        default="Authentication Service", description="API title"
    )
    auth_service_namespace: str = Field(
        default="backend",
        description="Logical namespace or domain for the service",
    )
    auth_service_version: str = Field(default="1.0.0", description="API version")
    auth_service_deployment_env: str = Field(
        default="production",
        description="Deployment environment (e.g. production, staging, dev)",
    )

    # Observability
    otel_exporter_otlp_endpoint: str | None = Field(
        default=None,
        description="OTLP collector endpoint (e.g., http://otel-collector:4317)",
    )

    # Auth Service Database URI
    auth_service_database_uri: SecretStr = Field(..., description="Database URI")

    # Supabase credentials
    auth_service_supabase_url: str = Field(..., description="Supabase URL")
    auth_service_supabase_publishable_key: str = Field(
        ..., description="Supabase publishable API Key"
    )
    auth_service_supabase_secret_key: SecretStr = Field(
        ..., description="Supabase secret API Key"
    )
    auth_service_supabase_jwt_signing_key_discovery_url: str = Field(
        ..., description="Supabase JWT signing key discovery URL"
    )

    # Auth tenant invitation
    auth_service_tenant_invitation_secret_key: SecretStr = Field(
        ..., description="Tenant invitation secret key"
    )

    # Redpanda
    redpanda_bootstrap_servers: str = Field(
        ...,
        description="Comma-separated list of Redpanda bootstrap brokers (e.g. 'localhost:19092,localhost:19093')",
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
