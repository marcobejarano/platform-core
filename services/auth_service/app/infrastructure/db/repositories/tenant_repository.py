from uuid import UUID

from sqlalchemy import exists, select

from services.auth_service.app.domain.tenants.models import (
    Tenant,
)
from services.auth_service.app.domain.tenants.repository import (
    TenantRepository,
)
from services.auth_service.app.infrastructure.db.models.tenant import (
    TenantModel,
)
from services.auth_service.app.infrastructure.db.repositories.base import (
    SqlAlchemyAggregateRepository,
)


class SqlAlchemyTenantRepository(
    SqlAlchemyAggregateRepository[Tenant, TenantModel],
    TenantRepository,
):
    """
    SQLAlchemy implementation of TenantRepository.
    Inherits aggregate tracking behavior.
    """

    # -------------------------------------------------
    # Commands
    # -------------------------------------------------

    async def add(self, tenant: Tenant) -> None:
        model = TenantModel.from_domain(tenant)
        self._session.add(model)

        # Track new aggregate
        self._track(tenant, model)

    # -------------------------------------------------
    # Queries
    # -------------------------------------------------

    async def get(self, tenant_id: UUID) -> Tenant | None:
        model = await self._session.get(TenantModel, tenant_id)

        if model is None:
            return None

        tenant = model.to_domain()

        # Track aggregate + ORM model for sync
        self._track(tenant, model)

        return tenant

    async def exists(self, tenant_id: UUID) -> bool:
        stmt = select(exists().where(TenantModel.id == tenant_id))
        result = await self._session.execute(stmt)
        return result.scalar_one()
