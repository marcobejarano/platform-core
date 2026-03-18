from uuid import UUID

from pydantic import BaseModel, EmailStr


class SignupRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class AuthUpdateRequest(BaseModel):
    display_name: str | None = None
    phone: str | None = None


class MessageResponse(BaseModel):
    message: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class MeResponse(BaseModel):
    user_id: UUID


class AuthResponse(BaseModel):
    email: EmailStr
    display_name: str | None

    @classmethod
    def from_supabase(cls, user) -> "AuthResponse | None":
        if not user:
            return None

        # user can be dict or Supabase User object
        metadata = getattr(user, "user_metadata", None) or user.get("user_metadata", {})

        return cls(
            email=getattr(user, "email", None) or user.get("email"),
            display_name=metadata.get("display_name"),
        )
