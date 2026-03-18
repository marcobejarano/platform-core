from uuid import UUID

from services.auth_service.app.application.unit_of_work import UnitOfWork
from services.auth_service.app.domain.tenant_memberships.models import (
    MembershipRole,
    TenantMembership,
)


class TenantMembershipService:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    # -------------------------------------------------
    # Commands
    # -------------------------------------------------

    async def add_owner(
        self,
        *,
        tenant_id: UUID,
        user_id: UUID,
    ) -> None:

        async with self._uow as uow:
            if not await uow.tenants.exists(tenant_id):
                raise ValueError("Tenant not found")

            if await uow.memberships.exists_by_user_and_role(
                user_id=user_id,
                role=MembershipRole.OWNER,
            ):
                raise ValueError("User already owns a workspace")

            membership = TenantMembership.create_owner(
                tenant_id=tenant_id,
                user_id=user_id,
            )

            await uow.memberships.add(membership)

    async def add_member(
        self,
        *,
        tenant_id: UUID,
        user_id: UUID,
        role: MembershipRole = MembershipRole.MEMBER,
    ) -> None:

        async with self._uow as uow:
            if not await uow.tenants.exists(tenant_id):
                raise ValueError("Tenant not found")

            existing = await uow.memberships.get(
                tenant_id=tenant_id,
                user_id=user_id,
            )

            if existing:
                raise ValueError("User already member of this workspace")

            membership = TenantMembership.create_member(
                tenant_id=tenant_id,
                user_id=user_id,
                role=role,
            )

            await uow.memberships.add(membership)

    async def change_role(
        self,
        *,
        tenant_id: UUID,
        user_id: UUID,
        new_role: MembershipRole,
    ) -> None:

        async with self._uow as uow:
            membership = await uow.memberships.get(
                tenant_id=tenant_id,
                user_id=user_id,
            )

            if membership is None:
                raise ValueError("Membership not found")

            membership.change_role(new_role)

    async def deactivate_member(
        self,
        *,
        tenant_id: UUID,
        user_id: UUID,
    ) -> None:

        async with self._uow as uow:
            membership = await uow.memberships.get(
                tenant_id=tenant_id,
                user_id=user_id,
            )

            if membership is None:
                raise ValueError("Membership not found")

            membership.deactivate()

    # -------------------------------------------------
    # Queries
    # -------------------------------------------------

    async def get(
        self,
        *,
        tenant_id: UUID,
        user_id: UUID,
    ) -> TenantMembership | None:

        async with self._uow as uow:
            return await uow.memberships.get(
                tenant_id=tenant_id,
                user_id=user_id,
            )

    async def ensure_owner_tenant(self, user_id: UUID):

        async with self._uow as uow:
            membership = await uow.memberships.get_active_owner_by_user(user_id)

            if membership is None:
                raise ValueError("User does not own any workspace")

            tenant = await uow.tenants.get(membership.tenant_id)

            if tenant is None:
                raise ValueError("Owner tenant not found")

            return tenant

    async def list_members(self, tenant_id: UUID):

        async with self._uow as uow:
            return await uow.memberships.list_active_by_tenant(tenant_id)

    async def get_owner(self, user_id: UUID):

        async with self._uow as uow:
            return await uow.memberships.get_active_owner_by_user(user_id)
