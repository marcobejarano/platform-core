from uuid import UUID

from pydantic import BaseModel, EmailStr

from services.auth_service.app.domain.tenant_memberships.models import MembershipRole


class InviteUserRequest(BaseModel):
    tenant_id: UUID
    email: EmailStr
    role: MembershipRole


class AcceptInvitationRequest(BaseModel):
    token: str


class InvitationCreatedResponse(BaseModel):
    token: str
    status: str


class InvitationPreviewResponse(BaseModel):
    tenant_id: UUID
    email: EmailStr
    role: MembershipRole
    expires_at: str


class MessageResponse(BaseModel):
    message: str
