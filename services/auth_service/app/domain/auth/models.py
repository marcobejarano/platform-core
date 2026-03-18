from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AuthSession:
    user_id: UUID
    email: str
    access_token: str
    refresh_token: str


@dataclass(frozen=True)
class AuthenticatedUser:
    id: UUID
    email: str
