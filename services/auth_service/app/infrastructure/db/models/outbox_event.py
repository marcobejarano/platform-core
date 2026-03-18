from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import JSON, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from services.auth_service.app.infrastructure.db.base import BaseModel, TimestampMixin


class OutboxEventModel(BaseModel, TimestampMixin):
    """
    Transactional Outbox table.

    Guarantees:
    - Event is saved in same DB transaction as domain write
    - Reliable publishing to Redpanda
    - Retry-safe
    - Horizontally scalable
    """

    __tablename__ = "outbox_events"

    # What happened (ex: tenant.invitation.created)
    event_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    # JSON payload of event
    payload: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    # Optional routing key (ex: tenant_id or invitation_id)
    aggregate_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
        index=True,
    )

    # Publishing status
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    # Retry handling
    retry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # Last error message (if failed)
    last_error: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )

    # Optional: for ordering guarantees
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
