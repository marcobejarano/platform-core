from uuid import UUID

from sqlalchemy import exists, select

from services.auth_service.app.domain.tenant_memberships.models import (
    MembershipRole,
    TenantMembership,
)
from services.auth_service.app.domain.tenant_memberships.repository import (
    TenantMembershipRepository,
)
from services.auth_service.app.infrastructure.db.models.tenant_membership import (
    TenantMembershipModel,
)
from services.auth_service.app.infrastructure.db.repositories.base import (
    SqlAlchemyAggregateRepository,
)


class SqlAlchemyTenantMembershipRepository(
    SqlAlchemyAggregateRepository[TenantMembership, TenantMembershipModel],
    TenantMembershipRepository,
):
    """
    SQLAlchemy implementation of TenantMembershipRepository.
    Inherits aggregate tracking behavior.
    """

    # -------------------------------------------------
    # Commands
    # -------------------------------------------------

    async def add(self, membership: TenantMembership) -> None:
        model = TenantMembershipModel.from_domain(membership)

        self._session.add(model)

        # Track new aggregate (no ORM model sync needed)
        self._track(membership, model)

    # -------------------------------------------------
    # Queries
    # -------------------------------------------------

    async def get(
        self,
        *,
        tenant_id: UUID,
        user_id: UUID,
    ) -> TenantMembership | None:
        stmt = select(TenantMembershipModel).where(
            TenantMembershipModel.tenant_id == tenant_id,
            TenantMembershipModel.user_id == user_id,
            TenantMembershipModel.is_active.is_(True),
        )

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        domain = model.to_domain()

        # Track pair for UnitOfWork synchronization
        self._track(domain, model)

        return domain

    async def list_active_by_tenant(
        self,
        tenant_id: UUID,
    ) -> list[TenantMembership]:
        stmt = select(TenantMembershipModel).where(
            TenantMembershipModel.tenant_id == tenant_id,
            TenantMembershipModel.is_active.is_(True),
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        memberships: list[TenantMembership] = []

        for model in models:
            domain = model.to_domain()
            self._track(domain, model)
            memberships.append(domain)

        return memberships

    async def get_active_owner_by_user(
        self,
        user_id: UUID,
    ) -> TenantMembership | None:
        stmt = select(TenantMembershipModel).where(
            TenantMembershipModel.user_id == user_id,
            TenantMembershipModel.role == MembershipRole.OWNER,
            TenantMembershipModel.is_active.is_(True),
        )

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        domain = model.to_domain()

        self._track(domain, model)

        return domain

    async def exists_by_user_and_role(
        self,
        *,
        user_id: UUID,
        role: MembershipRole,
    ) -> bool:
        stmt = select(
            exists().where(
                TenantMembershipModel.user_id == user_id,
                TenantMembershipModel.role == role,
                TenantMembershipModel.is_active.is_(True),
            )
        )

        result = await self._session.execute(stmt)
        return result.scalar_one()
