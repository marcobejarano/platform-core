from typing import Generic, List, Set, Tuple, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from services.auth_service.app.domain.shared.aggregate_root import AggregateRoot

DomainT = TypeVar("DomainT", bound=AggregateRoot)
ModelT = TypeVar("ModelT")


class SqlAlchemyAggregateRepository(Generic[DomainT, ModelT]):
    """
    Base repository for AggregateRoot repositories.

    Responsibilities:
    - Hold AsyncSession
    - Track aggregates for event collection
    - Track (domain, orm_model) pairs for synchronization
    """

    def __init__(self, session: AsyncSession):
        self._session = session
        self._seen: Set[DomainT] = set()
        self._tracked_pairs: List[Tuple[DomainT, ModelT]] = []

    # -------------------------------------------------
    # Tracking
    # -------------------------------------------------

    def _track(self, aggregate: DomainT, model: ModelT) -> None:
        """
        Track an aggregate and its ORM model for UnitOfWork synchronization
        and domain event collection.
        """
        if aggregate not in self._seen:
            self._seen.add(aggregate)
            self._tracked_pairs.append((aggregate, model))

    # -------------------------------------------------
    # Exposed to UnitOfWork
    # -------------------------------------------------

    @property
    def seen(self) -> Set[DomainT]:
        return set(self._seen)

    @property
    def tracked_pairs(self) -> List[Tuple[DomainT, ModelT]]:
        return list(self._tracked_pairs)

    def clear_tracking(self) -> None:
        self._seen.clear()
        self._tracked_pairs.clear()
