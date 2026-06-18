"""Async database engine and session factory for the analytics service."""

from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings

settings = get_settings()
# Bounded pool + server-side timeouts so a hung query/transaction can't pin a
# connection (and its locks) indefinitely, and the per-instance connection count
# stays predictable against the shared Postgres max_connections budget. The events
# consumer runs as a separate process with its own pool — budget accordingly.
engine: AsyncEngine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
    pool_recycle=1800,
    connect_args={
        "options": (
            "-c statement_timeout=30000 "
            "-c idle_in_transaction_session_timeout=60000"
        ),
    },
)
SessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency yielding an async session bound to the request scope."""
    async with SessionLocal() as session:
        yield session
