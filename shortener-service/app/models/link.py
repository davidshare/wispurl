from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Link(Base):
    __tablename__ = "links"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    short_code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    long_url: Mapped[str] = mapped_column(String(2048))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(default=True, server_default="true")

    # Partial index supporting the Cleanup service's expiry sweep
    # (WHERE is_active AND expires_at < now()) so it never seq-scans the table.
    __table_args__ = (
        Index(
            "ix_links_active_expiry",
            "expires_at",
            postgresql_where=text("is_active"),
        ),
    )
