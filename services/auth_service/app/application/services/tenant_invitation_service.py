from uuid import UUID

from services.auth_service.app.application.unit_of_work import UnitOfWork
from services.auth_service.app.domain.tenant_invitations.models import (
    TenantInvitation,
)
from services.auth_service.app.domain.tenant_memberships.models import (
    MembershipRole,
    TenantMembership,
)
from services.auth_service.app.domain.user_profiles.models import UserProfile


class TenantInvitationService:
    """
    Application service responsible for:

    - Inviting users to a tenant
    - Accepting invitations
    - Public preview validation
    """

    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    # -------------------------------------------------
    # Invite User
    # -------------------------------------------------

    async def invite_user(
        self,
        *,
        tenant_id: UUID,
        email: str,
        role: MembershipRole,
        invited_by_user_id: UUID,
    ) -> TenantInvitation:

        async with self._uow as uow:
            membership = await uow.memberships.get(
                tenant_id=tenant_id,
                user_id=invited_by_user_id,
            )

            if not membership:
                raise PermissionError("You are not a member of this tenant")

            if membership.role not in {
                MembershipRole.OWNER,
                MembershipRole.ADMIN,
            }:
                raise PermissionError("You do not have permission to invite users")

            if membership.role == MembershipRole.ADMIN and role == MembershipRole.OWNER:
                raise PermissionError("Admins cannot invite owners")

            existing = await uow.invitations.get_pending_by_email(
                tenant_id=tenant_id,
                email=email.lower(),
            )

            if existing:
                raise ValueError("There is already a pending invitation for this email")

            invitation = TenantInvitation.create(
                tenant_id=tenant_id,
                email=email.lower(),
                role=role,
                invited_by_user_id=invited_by_user_id,
            )

            await uow.invitations.add(invitation)

            return invitation

    # -------------------------------------------------
    # Accept Invitation
    # -------------------------------------------------

    async def accept_invitation(
        self,
        *,
        invitation_id: UUID,
        user_id: UUID,
        user_email: str,
    ) -> None:

        async with self._uow as uow:
            invitation = await uow.invitations.get_by_id(invitation_id)

            if not invitation:
                raise ValueError("Invitation not found")

            if invitation.is_accepted:
                raise ValueError("Invitation already accepted")

            if invitation.is_revoked:
                raise ValueError("Invitation has been revoked")

            if invitation.is_expired():
                invitation.expire()
                await uow.commit()
                raise ValueError("Invitation has expired")

            if invitation.email.lower() != user_email.lower():
                raise PermissionError("You cannot accept this invitation")

            existing_membership = await uow.memberships.get(
                tenant_id=invitation.tenant_id,
                user_id=user_id,
            )

            if existing_membership:
                raise ValueError("User is already a member of this tenant")

            # Accept invitation (mutates aggregate)
            invitation.accept()

            # Create membership
            if invitation.role == MembershipRole.OWNER:
                membership = TenantMembership.create_owner(
                    tenant_id=invitation.tenant_id,
                    user_id=user_id,
                )

            else:
                membership = TenantMembership.create_member(
                    tenant_id=invitation.tenant_id,
                    user_id=user_id,
                    role=invitation.role,
                )

            await uow.memberships.add(membership)

            existing_profile = await uow.profiles.get_by_user_and_tenant(
                user_id=user_id,
                tenant_id=invitation.tenant_id,
            )

            if not existing_profile:
                profile = UserProfile.create(
                    user_id=user_id,
                    tenant_id=invitation.tenant_id,
                )

                await uow.profiles.add(profile)

    # -------------------------------------------------
    # Preview Invitation
    # -------------------------------------------------

    async def get_invitation_for_preview(
        self,
        invitation_id: UUID,
    ) -> TenantInvitation:

        async with self._uow as uow:
            invitation = await uow.invitations.get_by_id(invitation_id)

            if not invitation:
                raise ValueError("Invitation not found")

            if invitation.is_accepted:
                raise ValueError("Invitation already accepted")

            if invitation.is_revoked:
                raise ValueError("Invitation has been revoked")

            if invitation.is_expired():
                invitation.expire()
                await uow.commit()
                raise ValueError("Invitation has expired")

            return invitation
