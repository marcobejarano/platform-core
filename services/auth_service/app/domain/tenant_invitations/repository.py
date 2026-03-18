from abc import ABC, abstractmethod
from uuid import UUID

from services.auth_service.app.domain.tenant_invitations.models import TenantInvitation


class TenantInvitationRepository(ABC):
    # -------------------------------------------------
    # Commands
    # -------------------------------------------------

    @abstractmethod
    async def add(self, invitation: TenantInvitation) -> None: ...

    # -------------------------------------------------
    # Queries
    # -------------------------------------------------

    @abstractmethod
    async def get_by_id(self, invitation_id: UUID) -> TenantInvitation | None: ...

    @abstractmethod
    async def get_pending_by_email(
        self,
        *,
        tenant_id: UUID,
        email: str,
    ) -> TenantInvitation | None: ...
