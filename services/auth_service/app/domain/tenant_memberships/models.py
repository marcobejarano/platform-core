from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID, uuid4

from services.auth_service.app.domain.shared.aggregate_root import AggregateRoot


class MembershipRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


@dataclass(eq=False)
class TenantMembership(AggregateRoot):
    id: UUID
    tenant_id: UUID
    user_id: UUID
    role: MembershipRole
    is_active: bool = True

    # -------------------------------------------------
    # Factory Methods
    # -------------------------------------------------

    @classmethod
    def create_owner(cls, *, tenant_id: UUID, user_id: UUID) -> "TenantMembership":
        membership = cls(
            id=uuid4(),
            tenant_id=tenant_id,
            user_id=user_id,
            role=MembershipRole.OWNER,
            is_active=True,
        )

        # membership._add_event(MembershipCreated(...))
        return membership

    @classmethod
    def create_member(
        cls,
        *,
        tenant_id: UUID,
        user_id: UUID,
        role: MembershipRole = MembershipRole.MEMBER,
    ) -> "TenantMembership":

        if role == MembershipRole.OWNER:
            raise ValueError("Owner must be created using create_owner()")

        membership = cls(
            id=uuid4(),
            tenant_id=tenant_id,
            user_id=user_id,
            role=role,
            is_active=True,
        )

        # membership._add_event(MembershipCreated(...))
        return membership

    # -------------------------------------------------
    # Behavior
    # -------------------------------------------------

    def deactivate(self) -> None:
        if not self.is_active:
            return

        self.is_active = False

        # self._add_event(MembershipDeactivated(...))

    def change_role(self, new_role: MembershipRole) -> None:
        if not self.is_active:
            raise ValueError("Cannot change role of inactive membership")

        self.role = new_role

        # self._add_event(MembershipRoleChanged(...))
