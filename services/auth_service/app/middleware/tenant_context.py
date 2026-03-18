from uuid import UUID

from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from services.auth_service.app.api.security.tokens import extract_access_token
from services.auth_service.app.application.services.tenant_membership_service import (
    TenantMembershipService,
)
from services.auth_service.app.application.services.tenant_service import TenantService
from services.auth_service.app.domain.auth.models import AuthenticatedUser
from services.auth_service.app.infrastructure.db.session import AsyncSessionLocal
from services.auth_service.app.infrastructure.db.unit_of_work import (
    SqlAlchemyUnitOfWork,
)
from services.auth_service.app.infrastructure.supabase.auth_service import (
    SupabaseAuthService,
)

bearer_scheme = HTTPBearer(auto_error=False)


class TenantContextMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, auth_service: SupabaseAuthService):
        super().__init__(app)
        self._auth = auth_service

    async def dispatch(self, request: Request, call_next):
        # -------------------------------------------------
        # Skip public routes
        # -------------------------------------------------
        if request.url.path.startswith("/api/v1/auth"):
            return await call_next(request)

        # -------------------------------------------------
        # Extract bearer token
        # -------------------------------------------------
        credentials = await bearer_scheme(request)
        try:
            access_token = extract_access_token(credentials)
        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
            )

        # -------------------------------------------------
        # Resolve authenticated user
        # -------------------------------------------------
        try:
            authenticated_user: AuthenticatedUser = await self._auth.me(
                access_token=access_token
            )
            user_id = authenticated_user.id
        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
            )

        # -------------------------------------------------
        # Open DB session
        # -------------------------------------------------
        async with AsyncSessionLocal() as session:
            try:
                uow = SqlAlchemyUnitOfWork(session)

                tenant_service = TenantService(uow)
                membership_service = TenantMembershipService(uow)

                # -----------------------------------------
                # Ensure owner tenant exists
                # -----------------------------------------
                owner_tenant = await membership_service.ensure_owner_tenant(
                    user_id=user_id
                )

                # -----------------------------------------
                # Resolve tenant
                # -----------------------------------------
                tenant_header = request.headers.get("X-Tenant-ID")

                if tenant_header:
                    try:
                        tenant_id = UUID(tenant_header)
                    except ValueError:
                        return JSONResponse(
                            status_code=400,
                            content={"detail": "Invalid X-Tenant-ID"},
                        )

                    tenant = await tenant_service.get_tenant(tenant_id)
                    if not tenant:
                        return JSONResponse(
                            status_code=404,
                            content={"detail": "Tenant not found"},
                        )

                    membership = await membership_service.get(
                        tenant_id=tenant.id,
                        user_id=user_id,
                    )
                    if not membership:
                        return JSONResponse(
                            status_code=403,
                            content={"detail": "User is not a member of this tenant"},
                        )
                else:
                    tenant = owner_tenant

                # -----------------------------------------
                # Attach context to request
                # -----------------------------------------
                request.state.user = authenticated_user
                request.state.user_id = user_id
                request.state.tenant = tenant
                request.state.tenant_id = tenant.id
                request.state.access_token = access_token

                await session.commit()

            except Exception:
                await session.rollback()
                raise

        return await call_next(request)
