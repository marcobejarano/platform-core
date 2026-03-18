from datetime import datetime, timezone
from typing import Iterable
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from services.auth_service.app.application.messaging.outbox_repository import (
    OutboxRepository,
)
from services.auth_service.app.infrastructure.db.models.outbox_event import (
    OutboxEventModel,
)


class SqlAlchemyOutboxRepository(OutboxRepository):
    """
    SQLAlchemy implementation of the OutboxRepository.
    Uses the same AsyncSession as other repositories to guarantee
    transactional consistency.
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    # -------------------------------------------------
    # Commands
    # -------------------------------------------------

    async def add(
        self,
        *,
        event_type: str,
        payload: dict,
        aggregate_id: UUID | None = None,
    ) -> None:
        event = OutboxEventModel(
            event_type=event_type,
            payload=payload,
            aggregate_id=aggregate_id,
        )

        self._session.add(event)

    # -------------------------------------------------
    # Queries
    # -------------------------------------------------

    async def list_unpublished(
        self,
        *,
        limit: int = 100,
    ) -> Iterable[OutboxEventModel]:
        stmt = (
            select(OutboxEventModel)
            .where(OutboxEventModel.published_at.is_(None))
            .order_by(OutboxEventModel.occurred_at.asc())
            .limit(limit)
            .with_for_update(skip_locked=True)
        )

        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def mark_as_published(
        self,
        *,
        event_id: UUID,
        published_at: datetime | None = None,
    ) -> None:
        if published_at is None:
            published_at = datetime.now(timezone.utc)

        stmt = (
            update(OutboxEventModel)
            .where(OutboxEventModel.id == event_id)
            .values(published_at=published_at)
        )

        await self._session.execute(stmt)

    async def increment_retry(
        self,
        *,
        event_id: UUID,
        error_message: str,
    ) -> None:
        stmt = (
            update(OutboxEventModel)
            .where(OutboxEventModel.id == event_id)
            .values(
                retry_count=OutboxEventModel.retry_count + 1,
                last_error=error_message,
            )
        )

        await self._session.execute(stmt)
