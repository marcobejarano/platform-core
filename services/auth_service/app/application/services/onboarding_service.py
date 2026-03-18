from uuid import UUID

from services.auth_service.app.application.unit_of_work import UnitOfWork
from services.auth_service.app.domain.tenant_memberships.models import (
    TenantMembership,
)
from services.auth_service.app.domain.tenants.models import Tenant
from services.auth_service.app.domain.user_profiles.models import UserProfile


class OnboardingService:
    """
    Orchestrates user bootstrap after successful authentication.

    Idempotent by design.
    """

    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    async def bootstrap_user(self, *, user_id: UUID, email: str) -> None:
        async with self._uow as uow:
            # -------------------------------------------------
            # 1️⃣ Ensure user has an owned workspace
            # -------------------------------------------------

            owner_membership = await uow.memberships.get_active_owner_by_user(user_id)

            if owner_membership:
                tenant_id = owner_membership.tenant_id
            else:
                workspace_name = f"{email.split('@')[0]}'s workspace"

                tenant = Tenant.create(name=workspace_name)

                await uow.tenants.add(tenant)

                membership = TenantMembership.create_owner(
                    tenant_id=tenant.id,
                    user_id=user_id,
                )

                await uow.memberships.add(membership)

                tenant_id = tenant.id

            # -------------------------------------------------
            # 2️⃣ Ensure user profile exists
            # -------------------------------------------------

            existing_profile = await uow.profiles.get_by_user_and_tenant(
                user_id=user_id,
                tenant_id=tenant_id,
            )

            if not existing_profile:
                profile = UserProfile.create(
                    user_id=user_id,
                    tenant_id=tenant_id,
                )

                await uow.profiles.add(profile)

            # -------------------------------------------------
            # Commit everything atomically
            # -------------------------------------------------

            await uow.commit()
