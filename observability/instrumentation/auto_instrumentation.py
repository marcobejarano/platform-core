import structlog
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor


def auto_instrument(app=None, engine=None, enable_http=True, enable_db=True):
    """
    Automatically instrument supported libraries with OpenTelemetry.

    :param app: FastAPI app instance
    :param engine: SQLAlchemy engine (sync or async)
    :param enable_http: Whether to instrument HTTP clients (requests/aiohttp)
    :param enable_db: Whether to instrument SQLAlchemy/AsyncPG
    """
    log = structlog.get_logger(__name__)

    if app:
        FastAPIInstrumentor.instrument_app(app)
        log.info("auto_instrumentation.fastapi_enabled")

    # if enable_http:
    #     RequestsInstrumentor().instrument()
    #     AioHttpClientInstrumentor().instrument()
    #     log.info("auto_instrumentation.http_clients_enabled")

    if enable_db and engine is not None:
        try:
            SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
            log.info("auto_instrumentation.sqlalchemy_enabled")
        except Exception:
            log.warning("auto_instrumentation.sqlalchemy_failed")

        try:
            AsyncPGInstrumentor().instrument()
            log.info("auto_instrumentation.asyncpg_enabled")
        except Exception:
            log.warning("auto_instrumentation.asyncpg_failed")
