from typing import List
from uuid import UUID

from services.auth_service.app.application.messaging.domain_event import DomainEvent


class AggregateRoot:
    """
    Base class for all aggregate roots.

    Responsibilities:
    - Record domain events
    - Expose events to application layer
    - Clear events after dispatch
    """

    id: UUID  # Expected on all aggregates

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    @property
    def _domain_events(self) -> List[DomainEvent]:
        # Lazy initialization (safe with dataclasses)
        if not hasattr(self, "_events"):
            self._events: List[DomainEvent] = []
        return self._events

    def _add_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def pull_events(self) -> tuple[DomainEvent, ...]:
        """
        Returns and clears recorded domain events.
        """
        events = tuple(self._domain_events)
        self._domain_events.clear()
        return events

    def has_events(self) -> bool:
        return bool(self._domain_events)
