from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterable
from uuid import UUID


class OutboxRepository(ABC):
    """
    Application-layer abstraction for transactional outbox.

    Defines what the application needs without leaking
    database or messaging implementation details.
    """

    # -------------------------------------------------
    # Commands
    # -------------------------------------------------

    @abstractmethod
    async def add(
        self,
        *,
        event_type: str,
        payload: dict,
        aggregate_id: UUID | None = None,
    ) -> None:
        """Persist a new outbox event inside the current transaction."""
        ...

    @abstractmethod
    async def mark_as_published(
        self,
        *,
        event_id: UUID,
        published_at: datetime,
    ) -> None:
        """Mark event as successfully published."""
        ...

    @abstractmethod
    async def increment_retry(
        self,
        *,
        event_id: UUID,
        error_message: str,
    ) -> None:
        """Increment retry counter and store last error."""
        ...

    # -------------------------------------------------
    # Queries
    # -------------------------------------------------

    @abstractmethod
    async def list_unpublished(
        self,
        *,
        limit: int = 100,
    ) -> Iterable:
        """Fetch unpublished events ordered by occurred_at."""
        ...
