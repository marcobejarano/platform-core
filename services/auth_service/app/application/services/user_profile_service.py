from uuid import UUID

from services.auth_service.app.application.unit_of_work import UnitOfWork
from services.auth_service.app.domain.user_profiles.models import UserProfile
from services.auth_service.app.exceptions.base import NotFoundException


class UserProfileService:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    async def get_for_user(
        self,
        *,
        user_id: UUID,
        tenant_id: UUID,
    ) -> UserProfile:
        async with self._uow as uow:
            profile = await uow.profiles.get_by_user_and_tenant(
                user_id=user_id,
                tenant_id=tenant_id,
            )
            if profile is None:
                raise NotFoundException(
                    resource="UserProfile",
                    identifier=f"user={user_id}, tenant={tenant_id}",
                )
            return profile

    async def create(
        self,
        *,
        user_id: UUID,
        tenant_id: UUID,
    ) -> UserProfile:
        async with self._uow as uow:
            existing = await uow.profiles.get_by_user_and_tenant(
                user_id=user_id,
                tenant_id=tenant_id,
            )
            if existing:
                raise ValueError("UserProfile already exists for this tenant")

            profile = UserProfile.create(
                user_id=user_id,
                tenant_id=tenant_id,
            )
            await uow.profiles.add(profile)
            return profile  # Commit happens automatically

    async def update(
        self,
        *,
        user_id: UUID,
        tenant_id: UUID,
        **fields,
    ) -> UserProfile:
        async with self._uow as uow:
            profile = await uow.profiles.get_by_user_and_tenant(
                user_id=user_id,
                tenant_id=tenant_id,
            )

            if profile is None:
                raise NotFoundException(
                    resource="UserProfile",
                    identifier=f"user={user_id}, tenant={tenant_id}",
                )

            profile.update(**fields)

            return profile  # No save(), commit persists changes

    async def ensure_exists(
        self,
        *,
        user_id: UUID,
        tenant_id: UUID,
    ) -> UserProfile:
        """
        Ensure a profile exists for (user_id, tenant_id).

        Idempotent:
        - Returns existing profile if present
        - Creates and returns profile if missing
        """
        async with self._uow as uow:
            existing = await uow.profiles.get_by_user_and_tenant(
                user_id=user_id,
                tenant_id=tenant_id,
            )

            if existing:
                return existing

            profile = UserProfile.create(
                user_id=user_id,
                tenant_id=tenant_id,
            )

            await uow.profiles.add(profile)
            return profile
