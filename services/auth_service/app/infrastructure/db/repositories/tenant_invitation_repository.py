from uuid import UUID

from sqlalchemy import select

from services.auth_service.app.domain.tenant_invitations.models import (
    TenantInvitation,
    TenantInvitationStatus,
)
from services.auth_service.app.domain.tenant_invitations.repository import (
    TenantInvitationRepository,
)
from services.auth_service.app.infrastructure.db.models.tenant_invitation import (
    TenantInvitationModel,
)
from services.auth_service.app.infrastructure.db.repositories.base import (
    SqlAlchemyAggregateRepository,
)


class SqlAlchemyTenantInvitationRepository(
    SqlAlchemyAggregateRepository[TenantInvitation, TenantInvitationModel],
    TenantInvitationRepository,
):
    """
    SQLAlchemy implementation of TenantInvitationRepository.
    Uses UnitOfWork aggregate tracking and synchronization.
    """

    # -------------------------------------------------
    # Commands
    # -------------------------------------------------

    async def add(self, invitation: TenantInvitation) -> None:
        model = TenantInvitationModel.from_domain(invitation)

        self._session.add(model)

        # Track new aggregate (no ORM sync needed)
        self._track(invitation, model)

    # -------------------------------------------------
    # Queries
    # -------------------------------------------------

    async def get_by_id(
        self,
        invitation_id: UUID,
    ) -> TenantInvitation | None:

        model = await self._session.get(
            TenantInvitationModel,
            invitation_id,
        )

        if model is None:
            return None

        domain = model.to_domain()

        # Track aggregate + ORM model for UnitOfWork sync
        self._track(domain, model)

        return domain

    async def get_pending_by_email(
        self,
        *,
        tenant_id: UUID,
        email: str,
    ) -> TenantInvitation | None:

        stmt = select(TenantInvitationModel).where(
            TenantInvitationModel.tenant_id == tenant_id,
            TenantInvitationModel.email == email,
            TenantInvitationModel.status == TenantInvitationStatus.PENDING,
        )

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        domain = model.to_domain()

        # Track aggregate + ORM model
        self._track(domain, model)

        return domain
