from abc import ABC, abstractmethod
from uuid import UUID

from services.auth_service.app.domain.tenant_memberships.models import (
    MembershipRole,
    TenantMembership,
)


class TenantMembershipRepository(ABC):
    # -------------------------------------------------
    # Commands
    # -------------------------------------------------

    @abstractmethod
    async def add(self, membership: TenantMembership) -> None:
        """
        Persist a membership (insert or update).
        """
        ...

    # -------------------------------------------------
    # Queries
    # -------------------------------------------------

    @abstractmethod
    async def get(
        self,
        *,
        tenant_id: UUID,
        user_id: UUID,
    ) -> TenantMembership | None:
        """
        Return membership for a given user inside a tenant.
        """
        ...

    @abstractmethod
    async def list_active_by_tenant(
        self,
        tenant_id: UUID,
    ) -> list[TenantMembership]:
        """
        Return all active memberships of a tenant.
        """
        ...

    @abstractmethod
    async def get_active_owner_by_user(
        self,
        user_id: UUID,
    ) -> TenantMembership | None:
        """
        Return the membership where the user is OWNER.
        Assumes a user can own at most one workspace.
        """
        ...

    @abstractmethod
    async def exists_by_user_and_role(
        self,
        *,
        user_id: UUID,
        role: MembershipRole,
    ) -> bool:
        """
        Check if a user has a membership with a specific role.
        """
        ...
