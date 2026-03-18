from fastapi import APIRouter, Request

from services.auth_service.app.schemas.api.context import RequestContextResponse

router = APIRouter(prefix="/context", tags=["context"])


@router.get("/current", response_model=RequestContextResponse)
async def get_context(request: Request) -> RequestContextResponse:
    return RequestContextResponse(
        user_id=request.state.user_id,
        tenant_id=request.state.tenant_id,
    )
