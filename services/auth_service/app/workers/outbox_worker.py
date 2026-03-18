import asyncio
import signal

import structlog
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from services.auth_service.app.infrastructure.messaging.event_publisher import (
    EventPublisher,
)
from services.auth_service.app.infrastructure.messaging.outbox_dispatcher import (
    OutboxDispatcher,
)
from services.auth_service.app.infrastructure.messaging.redpanda_producer import (
    RedpandaProducer,
)
from services.auth_service.app.settings import settings


logger = structlog.get_logger(__name__)


async def main() -> None:
    logger.info("outbox_worker.starting", service="auth-service")

    # -------------------------------------------------
    # Database
    # -------------------------------------------------

    logger.info("outbox_worker.db_connecting")

    engine = create_async_engine(
        settings.auth_service_database_uri.get_secret_value(),
        pool_size=10,
        max_overflow=20,
    )

    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    logger.info("outbox_worker.db_ready")

    # -------------------------------------------------
    # Kafka / Redpanda Producer
    # -------------------------------------------------

    logger.info(
        "outbox_worker.kafka_starting",
        bootstrap_servers=settings.redpanda_bootstrap_servers,
    )

    producer = RedpandaProducer(settings.redpanda_bootstrap_servers)
    await producer.start()

    logger.info("outbox_worker.kafka_connected")

    publisher = EventPublisher(
        producer=producer,
        producer_name="auth-service",
    )

    dispatcher = OutboxDispatcher(
        session_factory=session_factory,
        publisher=publisher,
        poll_interval=1.0,
    )

    logger.info(
        "outbox_worker.dispatcher_started",
        poll_interval=1.0,
    )

    # -------------------------------------------------
    # Graceful shutdown
    # -------------------------------------------------

    stop_event = asyncio.Event()

    def shutdown():
        logger.info("outbox_worker.shutdown_signal_received")
        stop_event.set()

    loop = asyncio.get_running_loop()

    # Windows-safe signal handling
    try:
        loop.add_signal_handler(signal.SIGINT, shutdown)
        loop.add_signal_handler(signal.SIGTERM, shutdown)
    except NotImplementedError:
        pass

    dispatcher_task = asyncio.create_task(dispatcher.run())

    try:
        await stop_event.wait()

    finally:
        logger.info("outbox_worker.stopping_dispatcher")

        dispatcher_task.cancel()

        try:
            await dispatcher_task
        except asyncio.CancelledError:
            pass

        logger.info("outbox_worker.kafka_stopping")
        await producer.stop()

        logger.info("outbox_worker.db_disposing")
        await engine.dispose()

        logger.info("outbox_worker.stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("outbox_worker.keyboard_interrupt")


# How It Runs in Production
# You run it as a separate process, not inside the API.
# Example commands:
# python -m services.auth_service.app.workers.outbox_worker
# Now you have two services running:
# * auth-api
# * auth-outbox-worker
# They share the same database.
