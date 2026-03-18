from fastapi import APIRouter, Depends, Request

from services.auth_service.app.api.dependencies.services import (
    get_complete_profile_service,
    get_user_profile_service,
)
from services.auth_service.app.application.services.complete_profile_service import (
    CompleteProfileService,
)
from services.auth_service.app.application.services.user_profile_service import (
    UserProfileService,
)
from services.auth_service.app.schemas.api.auth import AuthResponse
from services.auth_service.app.schemas.api.complete_profile import (
    CompleteProfileRequest,
    CompleteProfileResponse,
)
from services.auth_service.app.schemas.api.profile import ProfileResponse

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    request: Request,
    profile_service: UserProfileService = Depends(get_user_profile_service),
):
    profile = await profile_service.get_for_user(
        user_id=request.state.user_id,
        tenant_id=request.state.tenant_id,
    )
    return ProfileResponse.from_domain(profile)


@router.patch(
    "/me",
    response_model=CompleteProfileResponse,
)
async def update_my_profile(
    payload: CompleteProfileRequest,
    request: Request,
    service: CompleteProfileService = Depends(get_complete_profile_service),
):
    profile, auth_user = await service.update(
        user_id=request.state.user_id,
        tenant_id=request.state.tenant_id,
        access_token=request.state.access_token,
        profile_data=payload.profile.model_dump(exclude_unset=True)
        if payload.profile
        else None,
        auth_data=payload.auth.model_dump(exclude_unset=True) if payload.auth else None,
    )

    return CompleteProfileResponse(
        profile=ProfileResponse.from_domain(profile),
        auth=AuthResponse.from_supabase(auth_user),
    )
