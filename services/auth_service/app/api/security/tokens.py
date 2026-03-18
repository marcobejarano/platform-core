from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials


def extract_access_token(
    credentials: HTTPAuthorizationCredentials | None,
) -> str:
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header",
        )

    return credentials.credentials
