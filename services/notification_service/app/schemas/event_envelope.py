from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class EventEnvelope(BaseModel):
    event_id: UUID
    event_type: str
    occurred_at: datetime
    producer: str
    schema_version: int
    payload: dict[str, Any]
