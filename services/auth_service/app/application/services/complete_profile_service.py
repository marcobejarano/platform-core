from typing import Any
from uuid import UUID

from services.auth_service.app.application.services.user_profile_service import (
    UserProfileService,
)
from services.auth_service.app.domain.user_profiles.models import UserProfile
from services.auth_service.app.infrastructure.supabase.auth_service import (
    SupabaseAuthService,
)


class CompleteProfileService:
    def __init__(
        self,
        *,
        profile_service: UserProfileService,
        auth_service: SupabaseAuthService,
    ):
        self._profiles = profile_service
        self._auth = auth_service

    async def update(
        self,
        *,
        user_id: UUID,
        tenant_id: UUID,
        access_token: str,
        profile_data: dict | None,
        auth_data: dict | None,
    ) -> tuple[UserProfile, Any]:
        # ----------------------------
        # Update auth provider
        # ----------------------------
        auth_user = None
        if auth_data:
            auth_user = await self._auth.update_user(
                access_token=access_token,
                **auth_data,
            )

        # ----------------------------
        # Load profile
        # ----------------------------
        profile = await self._profiles.get_for_user(
            user_id=user_id,
            tenant_id=tenant_id,
        )

        # ----------------------------
        # Update domain profile
        # ----------------------------
        if profile_data:
            profile = await self._profiles.update(
                user_id=user_id,
                tenant_id=tenant_id,
                **profile_data,
            )

        return profile, auth_user
