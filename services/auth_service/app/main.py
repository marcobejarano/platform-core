from contextlib import asynccontextmanager

import structlog
from aiokafka import AIOKafkaProducer
from fastapi import FastAPI
from opentelemetry import trace

from observability.instrumentation.auto_instrumentation import auto_instrument
from services.auth_service.app.api.dependencies.services import get_auth_service
from services.auth_service.app.api.v1.routes import api_router
from services.auth_service.app.exceptions.setup import setup_exception_handling
from services.auth_service.app.infrastructure.db.session import (
    engine,
    test_connection,
)
from services.auth_service.app.infrastructure.security.supabase_jwt import (
    supabase_jwt_verifier,
)
from services.auth_service.app.middleware.tenant_context import TenantContextMiddleware
from services.auth_service.app.observability.setup import init_observability
from services.auth_service.app.settings import settings

tracer = trace.get_tracer("auth-service")
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Observability
    init_observability()
    auto_instrument(app=app, engine=engine)

    logger.info("observability_setup_completed", service="auth-service")
    logger.info("app.starting", service="auth-service")

    # ---- Infrastructure initialization ----
    with tracer.start_as_current_span("auth_db.health_check"):
        await test_connection()

    # 👉 Load Supabase JWKS here
    with tracer.start_as_current_span("auth.jwt.load_jwks"):
        await supabase_jwt_verifier.load_keys()

    logger.info("supabase_jwks_loaded", service="auth-service")

    # 🚀 Kafka / Redpanda Producer
    with tracer.start_as_current_span("auth.messaging.kafka_startup"):
        producer = AIOKafkaProducer(
            bootstrap_servers=settings.redpanda_bootstrap_servers,
            acks="all",  # safer for production
        )
        await producer.start()
        app.state.producer = producer

    logger.info("kafka_producer_started", service="auth-service")

    logger.info("app.ready", service="auth-service")

    # ---- Application runtime ----
    try:
        yield
    finally:
        logger.info("app.shutting_down", service="auth-service")

        # Stop Kafka producer gracefully
        producer: AIOKafkaProducer | None = getattr(app.state, "producer", None)
        if producer:
            with tracer.start_as_current_span("auth.messaging.kafka_shutdown"):
                await producer.stop()
            logger.info("kafka_producer_stopped", service="auth-service")

        await engine.dispose()

        logger.info("app.stopped", service="auth-service")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.auth_service_title,
        lifespan=lifespan,
    )

    # Exceptions
    setup_exception_handling(app)

    # Tenant context
    app.add_middleware(
        TenantContextMiddleware,
        auth_service=get_auth_service(),
    )

    # API routes
    app.include_router(api_router)

    return app


app = create_app()
