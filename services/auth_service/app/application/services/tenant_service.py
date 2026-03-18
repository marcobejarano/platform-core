from uuid import UUID

from services.auth_service.app.application.unit_of_work import UnitOfWork
from services.auth_service.app.domain.tenants.models import (
    Plan,
    Tenant,
)
from services.auth_service.app.exceptions.base import NotFoundException


class TenantService:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    # -------------------------------------------------
    # Commands
    # -------------------------------------------------

    async def create_tenant(self, tenant: Tenant) -> None:
        async with self._uow as uow:
            if await uow.tenants.exists(tenant.id):
                raise ValueError("Tenant already exists")

            await uow.tenants.add(tenant)

    async def update_plan(self, tenant_id: UUID, plan: Plan) -> None:
        async with self._uow as uow:
            tenant = await uow.tenants.get(tenant_id)

            if tenant is None:
                raise NotFoundException(
                    resource="Tenant",
                    identifier=str(tenant_id),
                )

            tenant.update_plan(plan)

    # -------------------------------------------------
    # Queries
    # -------------------------------------------------

    async def get_tenant(self, tenant_id: UUID) -> Tenant | None:
        async with self._uow as uow:
            return await uow.tenants.get(tenant_id)

    async def ensure_exists(self, tenant_id: UUID) -> None:
        async with self._uow as uow:
            if not await uow.tenants.exists(tenant_id):
                raise NotFoundException(
                    resource="Tenant",
                    identifier=str(tenant_id),
                )
