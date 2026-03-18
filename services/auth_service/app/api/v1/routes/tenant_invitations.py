from fastapi import APIRouter, Depends, HTTPException, status

from services.auth_service.app.api.dependencies.services import (
    get_current_user,
    get_invitation_token_service,
    get_tenant_invitation_service,
)
from services.auth_service.app.application.services.tenant_invitation_service import (
    TenantInvitationService,
)
from services.auth_service.app.domain.auth.models import AuthenticatedUser
from services.auth_service.app.infrastructure.security.invitation_token import (
    InvitationTokenService,
)
from services.auth_service.app.schemas.api.tenant_invitation import (
    AcceptInvitationRequest,
    InvitationCreatedResponse,
    InvitationPreviewResponse,
    InviteUserRequest,
    MessageResponse,
)

router = APIRouter(prefix="/tenant-invitations", tags=["tenant-invitations"])


@router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=InvitationCreatedResponse
)
async def invite_user(
    payload: InviteUserRequest,
    tenant_service: TenantInvitationService = Depends(get_tenant_invitation_service),
    token_service: InvitationTokenService = Depends(get_invitation_token_service),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    try:
        invitation = await tenant_service.invite_user(
            tenant_id=payload.tenant_id,
            email=payload.email,
            role=payload.role,
            invited_by_user_id=current_user.id,
        )

        token = token_service.generate(invitation.id)

        return InvitationCreatedResponse(
            token=token,
            status=invitation.status,
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/preview",
    response_model=InvitationPreviewResponse,
)
async def preview_invitation(
    token: str,
    tenant_service: TenantInvitationService = Depends(get_tenant_invitation_service),
    token_service: InvitationTokenService = Depends(get_invitation_token_service),
):
    try:
        invitation_id = token_service.verify(token)

        invitation = await tenant_service.get_invitation_for_preview(invitation_id)

        return InvitationPreviewResponse(
            tenant_id=invitation.tenant_id,
            email=invitation.email,
            role=invitation.role,
            expires_at=invitation.expires_at.isoformat(),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/accept",
    response_model=MessageResponse,
)
async def accept_invitation(
    payload: AcceptInvitationRequest,
    tenant_service: TenantInvitationService = Depends(get_tenant_invitation_service),
    token_service: InvitationTokenService = Depends(get_invitation_token_service),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    try:
        invitation_id = token_service.verify(payload.token)

        await tenant_service.accept_invitation(
            invitation_id=invitation_id,
            user_id=current_user.id,
            user_email=current_user.email,
        )

        return MessageResponse(message="Invitation accepted")

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
