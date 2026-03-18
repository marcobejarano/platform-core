from abc import ABC, abstractmethod
from uuid import UUID

from services.auth_service.app.domain.user_profiles.models import UserProfile


class UserProfileRepository(ABC):
    # -------------------------------------------------
    # Commands
    # -------------------------------------------------

    @abstractmethod
    async def add(self, profile: UserProfile) -> None: ...

    # -------------------------------------------------
    # Queries
    # -------------------------------------------------

    @abstractmethod
    async def get_by_user_and_tenant(
        self,
        *,
        user_id: UUID,
        tenant_id: UUID,
    ) -> UserProfile | None: ...
