from uuid import UUID

from sqlalchemy import Boolean, Enum, Index, and_
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from services.auth_service.app.domain.tenant_memberships.models import (
    MembershipRole,
)
from services.auth_service.app.domain.tenant_memberships.models import (
    TenantMembership as DomainMembership,
)
from services.auth_service.app.infrastructure.db.base import (
    BaseModel,
    TenantMixin,
    TimestampMixin,
)


class TenantMembershipModel(
    BaseModel,
    TenantMixin,
    TimestampMixin,
):
    __tablename__ = "tenant_memberships"

    # -------------------------------------------------
    # Columns
    # -------------------------------------------------

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    role: Mapped[MembershipRole] = mapped_column(
        Enum(MembershipRole, name="membership_role"),
        nullable=False,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        index=True,
    )

    # -------------------------------------------------
    # Constraints & Indexes
    # -------------------------------------------------

    __table_args__ = (
        # Only ONE active membership per user per tenant
        Index(
            "uq_active_tenant_user_membership",
            "tenant_id",
            "user_id",
            unique=True,
            postgresql_where=(is_active.is_(True)),
        ),
        # Only ONE active OWNER per tenant
        Index(
            "uq_active_owner_per_tenant",
            "tenant_id",
            unique=True,
            postgresql_where=and_(
                role == MembershipRole.OWNER,
                is_active.is_(True),
            ),
        ),
        # Only ONE active OWNER per user
        Index(
            "uq_active_owner_per_user",
            "user_id",
            unique=True,
            postgresql_where=and_(
                role == MembershipRole.OWNER,
                is_active.is_(True),
            ),
        ),
    )

    # -------------------------------------------------
    # Mapping helpers
    # -------------------------------------------------

    @classmethod
    def from_domain(
        cls,
        membership: DomainMembership,
    ) -> "TenantMembershipModel":
        return cls(
            id=membership.id,
            tenant_id=membership.tenant_id,
            user_id=membership.user_id,
            role=membership.role,
            is_active=membership.is_active,
        )

    def update_from_domain(
        self,
        membership: DomainMembership,
    ) -> None:
        self.role = membership.role
        self.is_active = membership.is_active

    def to_domain(self) -> DomainMembership:
        return DomainMembership(
            id=self.id,
            tenant_id=self.tenant_id,
            user_id=self.user_id,
            role=self.role,
            is_active=self.is_active,
        )
