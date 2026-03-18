import asyncio
import signal

import structlog

from services.notification_service.app.application.services.email_service import (
    EmailService,
)
from services.notification_service.app.application.templates.template_renderer import (
    TemplateRenderer,
)
from services.notification_service.app.infrastructure.email.ses_email_provider import (
    SESEmailProvider,
)
from services.notification_service.app.infrastructure.messaging.redpanda_consumer import (
    RedpandaConsumer,
)
from services.notification_service.app.infrastructure.messaging.topics import (
    TENANT_INVITATION_EVENTS_TOPIC,
)
from services.notification_service.app.schemas.email_event import (
    TenantInvitationCreatedEvent,
)
from services.notification_service.app.schemas.event_envelope import EventEnvelope
from services.notification_service.app.settings import settings

logger = structlog.get_logger()


async def main():
    logger.info("notification_worker.starting")

    provider = SESEmailProvider()
    renderer = TemplateRenderer()

    email_service = EmailService(
        provider=provider,
        renderer=renderer,
    )

    consumer = RedpandaConsumer(
        bootstrap_servers=settings.redpanda_bootstrap_servers,
        group_id=settings.redpanda_consumer_group,
        topics=[TENANT_INVITATION_EVENTS_TOPIC],
    )

    await consumer.start()

    async def handle_event(topic: str, payload: dict):
        envelope = EventEnvelope(**payload)

        if envelope.event_type == "tenant.invitation.created.v1":
            event = TenantInvitationCreatedEvent(**envelope.payload)
            await email_service.handle_tenant_invitation_created(event)

    stop_event = asyncio.Event()

    def shutdown():
        logger.info("notification_worker.shutdown_signal")
        stop_event.set()

    loop = asyncio.get_running_loop()
    try:
        loop.add_signal_handler(signal.SIGINT, shutdown)
        loop.add_signal_handler(signal.SIGTERM, shutdown)
    except NotImplementedError:
        pass

    consumer_task = asyncio.create_task(consumer.consume(handle_event))

    try:
        await stop_event.wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("notification_worker.interrupted")
    finally:
        logger.info("notification_worker.stopping_consumer")
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            pass
        await consumer.stop()
        logger.info("notification_worker.stopped")


if __name__ == "__main__":
    asyncio.run(main())

# How to run the worker:
# python -m services.notification_service.app.workers.email_worker
