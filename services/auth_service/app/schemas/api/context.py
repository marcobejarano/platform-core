from uuid import UUID
from pydantic import BaseModel


class RequestContextResponse(BaseModel):
    user_id: UUID
    tenant_id: UUID
