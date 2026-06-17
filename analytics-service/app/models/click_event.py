"""The ``click_events`` table: one row per recorded redirect click."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ClickEvent(Base):
    """A single click on a short link.

    ``short_code`` is stored as a plain indexed string, NOT a foreign key: links
    live in the Shortener's separate ``short_db``, so there is no cross-database FK.
    ``ip_address`` holds an ANONYMIZED value (see :func:`app.anonymize.anonymize_ip`),
    never the raw client IP.
    """

    __tablename__ = "click_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    short_code: Mapped[str] = mapped_column(String(32), index=True)
    clicked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    referrer: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Composite index for time-bucketed aggregation scoped to one short code.
    __table_args__ = (
        Index("ix_click_events_short_code_clicked_at", "short_code", "clicked_at"),
    )
