from pydantic import BaseModel

from services.auth_service.app.schemas.api.auth import AuthResponse, AuthUpdateRequest
from services.auth_service.app.schemas.api.profile import (
    ProfileResponse,
    ProfileUpdateRequest,
)


class CompleteProfileRequest(BaseModel):
    profile: ProfileUpdateRequest | None = None
    auth: AuthUpdateRequest | None = None

    model_config = {"extra": "forbid"}


class CompleteProfileResponse(BaseModel):
    profile: ProfileResponse
    auth: AuthResponse | None
