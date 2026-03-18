from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TenantInvitationCreatedEvent(BaseModel):
    id: UUID
    occurred_at: datetime
    invitation_id: UUID
    tenant_id: UUID
    email: str
    role: str
    invited_by_user_id: UUID
