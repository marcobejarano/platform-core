from dataclasses import asdict, dataclass
from datetime import datetime
from typing import ClassVar
from uuid import UUID


@dataclass(frozen=True)
class DomainEvent:
    EVENT_TYPE: ClassVar[str]

    id: UUID
    occurred_at: datetime

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if "EVENT_TYPE" not in cls.__dict__:
            raise TypeError(f"{cls.__name__} must define EVENT_TYPE class attribute")

    def to_payload(self) -> dict:
        data = asdict(self)

        def serialize(value):
            if isinstance(value, UUID):
                return str(value)
            if isinstance(value, datetime):
                return value.isoformat()
            return value

        return {k: serialize(v) for k, v in data.items()}
