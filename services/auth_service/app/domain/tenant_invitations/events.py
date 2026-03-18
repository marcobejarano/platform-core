from dataclasses import dataclass
from uuid import UUID

from services.auth_service.app.application.messaging.domain_event import DomainEvent


@dataclass(frozen=True)
class TenantInvitationCreated(DomainEvent):
    """
    Domain event emitted when a tenant invitation is created.
    """

    invitation_id: UUID
    tenant_id: UUID
    email: str
    role: str
    invited_by_user_id: UUID

    EVENT_TYPE = "tenant.invitation.created.v1"
