from sqlalchemy.ext.asyncio import AsyncSession

from services.auth_service.app.application.unit_of_work import UnitOfWork
from services.auth_service.app.infrastructure.db.repositories.outbox_repository import (
    SqlAlchemyOutboxRepository,
)
from services.auth_service.app.infrastructure.db.repositories.tenant_invitation_repository import (
    SqlAlchemyTenantInvitationRepository,
)
from services.auth_service.app.infrastructure.db.repositories.tenant_membership_repository import (
    SqlAlchemyTenantMembershipRepository,
)
from services.auth_service.app.infrastructure.db.repositories.tenant_repository import (
    SqlAlchemyTenantRepository,
)
from services.auth_service.app.infrastructure.db.repositories.user_profile_repository import (
    SqlAlchemyUserProfileRepository,
)


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        self.profiles = SqlAlchemyUserProfileRepository(self._session)
        self.tenants = SqlAlchemyTenantRepository(self._session)
        self.memberships = SqlAlchemyTenantMembershipRepository(self._session)
        self.invitations = SqlAlchemyTenantInvitationRepository(self._session)
        self.outbox = SqlAlchemyOutboxRepository(self._session)

        self._repositories = [
            self.profiles,
            self.tenants,
            self.memberships,
            self.invitations,
        ]
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if exc_type:
            await self.rollback()
        else:
            await self.commit()

        await self._session.close()

    # -------------------------------------------------
    # Aggregate Synchronization
    # -------------------------------------------------

    async def _sync_aggregates(self) -> None:
        for repo in self._repositories:
            for aggregate, model in repo.tracked_pairs:
                model.update_from_domain(aggregate)

    # -------------------------------------------------
    # Outbox Collection
    # -------------------------------------------------

    async def _collect_and_store_events(self) -> None:
        for repo in self._repositories:
            for aggregate in repo.seen:
                for event in aggregate.pull_events():
                    await self.outbox.add(
                        event_type=event.EVENT_TYPE,
                        payload=event.to_payload(),
                        aggregate_id=aggregate.id,
                    )

            repo.clear_tracking()

    # -------------------------------------------------
    # Transaction Control
    # -------------------------------------------------

    async def commit(self) -> None:
        # Sync domain → ORM
        await self._sync_aggregates()

        # Flush the session
        await self._session.flush()

        # Persist outbox events
        await self._collect_and_store_events()

        # Commit DB transaction
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
