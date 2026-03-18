from fastapi import APIRouter

from services.auth_service.app.api.v1.routes.auth import router as auth_router
from services.auth_service.app.api.v1.routes.context import router as context_router
from services.auth_service.app.api.v1.routes.profile import router as profile_router
from services.auth_service.app.api.v1.routes.tenant_invitations import (
    router as tenant_invitations_router,
)

api_v1 = APIRouter(prefix="/api/v1")
api_v1.include_router(auth_router)
api_v1.include_router(context_router)
api_v1.include_router(profile_router)
api_v1.include_router(tenant_invitations_router)

api_router = APIRouter()
api_router.include_router(api_v1)
