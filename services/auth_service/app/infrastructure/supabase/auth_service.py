from typing import cast
from uuid import UUID

import structlog
from fastapi import HTTPException, status
from jose import JWTError
from supabase_auth import UserAttributes

from services.auth_service.app.domain.auth.models import AuthenticatedUser, AuthSession
from services.auth_service.app.infrastructure.security.supabase_jwt import (
    supabase_jwt_verifier,
)
from services.auth_service.app.infrastructure.supabase.admin_client import (
    get_admin_supabase_client,
)
from services.auth_service.app.infrastructure.supabase.user_client import (
    get_user_supabase_client,
)

logger = structlog.get_logger(__name__)


class SupabaseAuthService:
    async def signup(self, *, email: str, password: str) -> None:
        supabase = get_admin_supabase_client()

        result = supabase.auth.sign_up(
            {
                "email": email,
                "password": password,
            }
        )

        if not result.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Signup failed"
            )

    async def login(self, *, email: str, password: str) -> AuthSession:
        supabase = get_admin_supabase_client()

        try:
            result = supabase.auth.sign_in_with_password(
                {
                    "email": email,
                    "password": password,
                }
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        if not result.user or not result.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        if not result.user.email:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User email missing",
            )

        return AuthSession(
            user_id=UUID(result.user.id),
            email=result.user.email.lower(),
            access_token=result.session.access_token,
            refresh_token=result.session.refresh_token,
        )

    async def me(self, *, access_token: str) -> AuthenticatedUser:
        try:
            payload = supabase_jwt_verifier.verify(access_token)
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        user_id = payload.get("sub")
        email = payload.get("email")

        if not user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        return AuthenticatedUser(
            id=UUID(user_id),
            email=email.lower(),
        )

    async def update_user(
        self,
        *,
        access_token: str,
        display_name: str | None = None,
    ):
        supabase = get_user_supabase_client(access_token)

        attributes: dict = {}

        if display_name is not None:
            attributes.setdefault("data", {})["display_name"] = display_name

        if not attributes:
            return

        result = supabase.auth.update_user(cast(UserAttributes, attributes))

        return result.user

    async def refresh(self, *, refresh_token: str) -> AuthSession:
        supabase = get_admin_supabase_client()

        try:
            result = supabase.auth.refresh_session(refresh_token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        if not result.user or not result.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        if not result.user.email:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User email missing",
            )

        return AuthSession(
            user_id=UUID(result.user.id),
            email=result.user.email.lower(),
            access_token=result.session.access_token,
            refresh_token=result.session.refresh_token,
        )

    async def logout(self, *, access_token: str) -> None:
        supabase = get_user_supabase_client(access_token)

        try:
            supabase.auth.sign_out()
        except Exception:
            # Logout must be idempotent
            pass
