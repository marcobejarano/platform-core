from uuid import UUID

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer


class InvitationTokenService:
    def __init__(self, secret_key: str):
        self._serializer = URLSafeTimedSerializer(secret_key)

    def generate(self, invitation_id: UUID) -> str:
        return self._serializer.dumps(str(invitation_id))

    def verify(self, token: str, max_age: int = 604800) -> UUID:
        try:
            invitation_id = self._serializer.loads(
                token,
                max_age=max_age,  # 7 days
            )
            return UUID(invitation_id)

        except SignatureExpired:
            raise ValueError("Invitation token expired")

        except BadSignature:
            raise ValueError("Invalid invitation token")
