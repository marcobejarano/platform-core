from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from services.auth_service.app.domain.tenant_invitations.models import (
    TenantInvitation as DomainTenantInvitation,
)
from services.auth_service.app.domain.tenant_invitations.models import (
    TenantInvitationStatus,
)
from services.auth_service.app.domain.tenant_memberships.models import MembershipRole
from services.auth_service.app.infrastructure.db.base import (
    BaseModel,
    TenantMixin,
    TimestampMixin,
)


class TenantInvitationModel(BaseModel, TenantMixin, TimestampMixin):
    __tablename__ = "tenant_invitations"

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    role: Mapped[MembershipRole] = mapped_column(
        Enum(MembershipRole, name="membership_role"),
        nullable=False,
    )

    invited_by_user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    status: Mapped[TenantInvitationStatus] = mapped_column(
        Enum(TenantInvitationStatus, name="tenant_invitation_status"),
        nullable=False,
        index=True,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    @classmethod
    def from_domain(
        cls,
        invitation: DomainTenantInvitation,
    ) -> "TenantInvitationModel":
        return cls(
            id=invitation.id,
            tenant_id=invitation.tenant_id,
            email=invitation.email,
            role=invitation.role,
            invited_by_user_id=invitation.invited_by_user_id,
            status=invitation.status,
            expires_at=invitation.expires_at,
        )

    def update_from_domain(
        self,
        invitation: DomainTenantInvitation,
    ) -> None:
        self.email = invitation.email
        self.role = invitation.role
        self.invited_by_user_id = invitation.invited_by_user_id
        self.status = invitation.status
        self.expires_at = invitation.expires_at

    def to_domain(self) -> DomainTenantInvitation:
        return DomainTenantInvitation(
            id=self.id,
            tenant_id=self.tenant_id,
            email=self.email,
            role=self.role,
            invited_by_user_id=self.invited_by_user_id,
            status=self.status,
            expires_at=self.expires_at,
            created_at=self.created_at,
        )
