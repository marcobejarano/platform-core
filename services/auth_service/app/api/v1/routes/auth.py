from fastapi import APIRouter, Depends, status

from services.auth_service.app.api.dependencies.auth import get_access_token
from services.auth_service.app.api.dependencies.services import (
    get_auth_service,
    get_onboarding_service,
)
from services.auth_service.app.application.services.onboarding_service import (
    OnboardingService,
)
from services.auth_service.app.infrastructure.supabase.auth_service import (
    SupabaseAuthService,
)
from services.auth_service.app.schemas.api.auth import (
    LoginRequest,
    MeResponse,
    MessageResponse,
    RefreshRequest,
    SignupRequest,
    TokenResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/signup", status_code=status.HTTP_201_CREATED, response_model=MessageResponse
)
async def signup(
    payload: SignupRequest,
    auth_service: SupabaseAuthService = Depends(get_auth_service),
):
    await auth_service.signup(
        email=payload.email,
        password=payload.password,
    )

    return MessageResponse(message="Signup successful. Please log in.")


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    auth_service: SupabaseAuthService = Depends(get_auth_service),
    onboarding_service: OnboardingService = Depends(get_onboarding_service),
):
    session = await auth_service.login(
        email=payload.email,
        password=payload.password,
    )

    await onboarding_service.bootstrap_user(
        user_id=session.user_id,
        email=session.email,
    )

    return TokenResponse(
        access_token=session.access_token,
        refresh_token=session.refresh_token,
    )


@router.get("/me", response_model=MeResponse)
async def me(
    access_token: str = Depends(get_access_token),
    auth_service: SupabaseAuthService = Depends(get_auth_service),
):
    authenticated_user = await auth_service.me(access_token=access_token)

    return MeResponse(user_id=authenticated_user.id)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest,
    auth_service: SupabaseAuthService = Depends(get_auth_service),
):
    session = await auth_service.refresh(refresh_token=payload.refresh_token)

    return TokenResponse(
        access_token=session.access_token,
        refresh_token=session.refresh_token,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    access_token: str = Depends(get_access_token),
    auth_service: SupabaseAuthService = Depends(get_auth_service),
):
    await auth_service.logout(access_token=access_token)

    return MessageResponse(message="Logged out")
