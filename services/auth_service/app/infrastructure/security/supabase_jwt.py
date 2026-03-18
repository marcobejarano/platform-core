from services.auth_service.app.infrastructure.security.supabase_jwt_verifier import (
    SupabaseJWTVerifier,
)
from services.auth_service.app.settings import settings

supabase_jwt_verifier = SupabaseJWTVerifier(
    jwks_url=settings.auth_service_supabase_jwt_signing_key_discovery_url
)
