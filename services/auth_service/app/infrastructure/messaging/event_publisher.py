from datetime import timezone

from services.auth_service.app.infrastructure.db.models.outbox_event import (
    OutboxEventModel,
)
from services.auth_service.app.infrastructure.messaging.event_envelope import (
    EventEnvelope,
)
from services.auth_service.app.infrastructure.messaging.redpanda_producer import (
    RedpandaProducer,
)
from services.auth_service.app.infrastructure.messaging.topics import (
    TENANT_INVITATION_EVENTS_TOPIC,
)

EVENT_TOPIC_MAP = {
    "tenant.invitation.created.v1": TENANT_INVITATION_EVENTS_TOPIC,
}


class EventPublisher:
    def __init__(self, producer: RedpandaProducer, producer_name: str):
        self._producer = producer
        self._producer_name = producer_name

    async def publish(self, event: OutboxEventModel) -> None:
        envelope = EventEnvelope(
            event_id=event.id,
            event_type=event.event_type,
            occurred_at=event.occurred_at.astimezone(timezone.utc),
            producer=self._producer_name,
            schema_version=1,
            payload=event.payload,
        )

        topic = EVENT_TOPIC_MAP.get(event.event_type)

        if topic is None:
            raise ValueError(f"No topic configured for event type {event.event_type}")

        await self._producer.send(
            topic,
            envelope.to_message(),
            key=str(event.payload["invitation_id"]).encode(),
        )
