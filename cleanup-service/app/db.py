"""Async engine and a minimal Core table mapping for ``short_db.links``.

DESIGN: the cleanup job connects to short_db DIRECTLY rather than calling a Shortener
HTTP endpoint. For a scheduled maintenance task this is acceptable and simpler — it
is a batch sweep, not request-path logic, and coupling it to the Shortener's
availability would defeat the point. The alternative (a Shortener internal
"expire" endpoint the job calls) is the right move once ownership of the write needs
to stay behind one service; noted here as the documented tradeoff.

Only the ``links`` columns this job needs are mapped, via SQLAlchemy Core, so the
service does not import the Shortener's ORM model across a service boundary.
"""

from __future__ import annotations

from sqlalchemy import Boolean, Column, DateTime, MetaData, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings

settings = get_settings()
engine: AsyncEngine = create_async_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

metadata = MetaData()

# Subset of short_db.links needed for the expiry sweep.
links_table = Table(
    "links",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("short_code", String(32)),
    Column("expires_at", DateTime(timezone=True)),
    Column("is_active", Boolean),
)
