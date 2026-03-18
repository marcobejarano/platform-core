from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from uuid import UUID, uuid4

from services.auth_service.app.domain.shared.aggregate_root import AggregateRoot
from services.auth_service.app.domain.tenant_invitations.events import (
    TenantInvitationCreated,
)
from services.auth_service.app.domain.tenant_memberships.models import MembershipRole


class TenantInvitationStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass(eq=False)
class TenantInvitation(AggregateRoot):
    id: UUID
    tenant_id: UUID
    email: str  # Invitee email (receiver)
    role: MembershipRole  # Role the invitee will get
    invited_by_user_id: UUID  # Inviter (sender)
    status: TenantInvitationStatus
    expires_at: datetime
    created_at: datetime | None = None

    # ------------------------
    # Factory
    # ------------------------

    @classmethod
    def create(
        cls,
        *,
        tenant_id: UUID,
        email: str,
        role: MembershipRole,
        invited_by_user_id: UUID,
        expires_in_days: int = 7,
    ) -> "TenantInvitation":

        if not email.strip():
            raise ValueError("Email cannot be empty")

        now = datetime.now(timezone.utc)

        invitation = cls(
            id=uuid4(),
            tenant_id=tenant_id,
            email=email.lower().strip(),
            role=role,
            invited_by_user_id=invited_by_user_id,
            status=TenantInvitationStatus.PENDING,
            expires_at=now + timedelta(days=expires_in_days),
            created_at=now,
        )

        # Emit domain event
        invitation._add_event(
            TenantInvitationCreated(
                id=uuid4(),
                occurred_at=now,
                invitation_id=invitation.id,
                tenant_id=tenant_id,
                email=invitation.email,
                role=role.value,
                invited_by_user_id=invited_by_user_id,
            )
        )

        return invitation

    # ------------------------
    # State transitions
    # ------------------------

    def accept(self) -> None:
        if self.status != TenantInvitationStatus.PENDING:
            raise ValueError("Only pending invitations can be accepted")

        if self.is_expired():
            raise ValueError("Invitation has expired")

        self.status = TenantInvitationStatus.ACCEPTED

    def revoke(self) -> None:
        if self.status != TenantInvitationStatus.PENDING:
            raise ValueError("Only pending invitations can be revoked")

        self.status = TenantInvitationStatus.REVOKED

    def expire(self) -> None:
        if self.status != TenantInvitationStatus.PENDING:
            return

        self.status = TenantInvitationStatus.EXPIRED

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at

    # ------------------------
    # Domain properties
    # ------------------------

    @property
    def is_pending(self) -> bool:
        return self.status == TenantInvitationStatus.PENDING

    @property
    def is_accepted(self) -> bool:
        return self.status == TenantInvitationStatus.ACCEPTED

    @property
    def is_revoked(self) -> bool:
        return self.status == TenantInvitationStatus.REVOKED

    @property
    def is_expired_status(self) -> bool:
        return self.status == TenantInvitationStatus.EXPIRED
