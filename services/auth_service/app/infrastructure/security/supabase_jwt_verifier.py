import httpx
from jose import JWTError, jwt


class SupabaseJWTVerifier:
    def __init__(self, *, jwks_url: str):
        self.jwks_url = jwks_url
        self._keys: dict[str, dict] = {}

    async def load_keys(self) -> None:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(self.jwks_url)
            resp.raise_for_status()

        jwks = resp.json()["keys"]
        self._keys = {key["kid"]: key for key in jwks}

    def verify(self, token: str) -> dict:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")

        if not kid or kid not in self._keys:
            raise JWTError("Unknown key id")

        key = self._keys[kid]

        return jwt.decode(
            token,
            key,  # Pass JWK directly
            algorithms=["ES256"],
            audience="authenticated",
            options={"verify_exp": True},
        )
