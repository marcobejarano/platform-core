import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker

from services.auth_service.app.infrastructure.db.repositories.outbox_repository import (
    SqlAlchemyOutboxRepository,
)
from services.auth_service.app.infrastructure.messaging.event_publisher import (
    EventPublisher,
)


class OutboxDispatcher:
    def __init__(
        self,
        session_factory: async_sessionmaker,
        publisher: EventPublisher,
        poll_interval: float = 1.0,
        concurrency: int = 20,
    ):
        self._session_factory = session_factory
        self._publisher = publisher
        self._poll_interval = poll_interval
        self._semaphore = asyncio.Semaphore(concurrency)

    async def _process_event(self, repo, event):
        async with self._semaphore:
            try:
                await self._publisher.publish(event)

                await repo.mark_as_published(event_id=event.id)

            except Exception as e:
                await repo.increment_retry(
                    event_id=event.id,
                    error_message=str(e),
                )

    async def run(self) -> None:
        while True:
            async with self._session_factory() as session:
                repo = SqlAlchemyOutboxRepository(session)

                events = await repo.list_unpublished(limit=100)

                if events:
                    tasks = [self._process_event(repo, event) for event in events]

                    await asyncio.gather(*tasks)

                    await session.commit()

            await asyncio.sleep(self._poll_interval)
