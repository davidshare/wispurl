"""The expiry sweep: deactivate expired links in batches.

Idempotent by construction: only rows that are still ``is_active`` AND past their
``expires_at`` are selected, so a deactivated link is never touched again — re-running
the sweep is a no-op.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select, update

from app.db import SessionLocal, links_table


async def sweep_expired_links(batch_size: int) -> list[str]:
    """Deactivate all currently-expired active links, in batches.

    Returns the short codes of the links deactivated in this run (across all
    batches), so the caller can publish a ``link.expired`` event per code.
    """
    deactivated: list[str] = []

    while True:
        async with SessionLocal() as session:
            rows = await session.execute(
                select(links_table.c.id, links_table.c.short_code)
                .where(
                    links_table.c.is_active.is_(True),
                    links_table.c.expires_at.is_not(None),
                    links_table.c.expires_at < func.now(),
                )
                .limit(batch_size),
            )
            batch = rows.all()
            if not batch:
                return deactivated

            ids: list[UUID] = [row.id for row in batch]
            await session.execute(
                update(links_table)
                .where(links_table.c.id.in_(ids))
                .values(is_active=False),
            )
            await session.commit()

            deactivated.extend(row.short_code for row in batch)

        # A short batch means we've drained the backlog for this run.
        if len(batch) < batch_size:
            return deactivated
