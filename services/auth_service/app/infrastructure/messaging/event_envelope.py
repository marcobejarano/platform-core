import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import UUID


@dataclass
class EventEnvelope:
    event_id: UUID
    event_type: str
    occurred_at: datetime
    producer: str
    schema_version: int
    payload: dict[str, Any]

    def to_message(self) -> bytes:
        data = asdict(self)

        # Convert UUID and datetime to strings
        data["event_id"] = str(self.event_id)
        data["occurred_at"] = self.occurred_at.astimezone(timezone.utc).isoformat()

        return json.dumps(data).encode("utf-8")
