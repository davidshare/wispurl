"""All ``click_events`` queries: a single insert plus SQL-side aggregations.

Aggregation is performed in the database with ``GROUP BY`` (never in Python), and
every query is parameterized through SQLAlchemy expressions.
"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.click_event import ClickEvent


class ClickEventRepository:
    """Reads and writes for the ``click_events`` table."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        short_code: str,
        ip_address: str | None,
        referrer: str | None,
        user_agent: str | None,
        clicked_at: datetime | None,
    ) -> ClickEvent:
        """Insert one click row, letting the DB default ``clicked_at`` when absent."""
        values: dict[str, object] = {
            "short_code": short_code,
            "ip_address": ip_address,
            "referrer": referrer,
            "user_agent": user_agent,
        }
        if clicked_at is not None:
            values["clicked_at"] = clicked_at
        event = ClickEvent(**values)
        self._session.add(event)
        await self._session.flush()
        return event

    async def count_total(self, short_code: str) -> int:
        """Return the total number of clicks recorded for ``short_code``."""
        result = await self._session.execute(
            select(func.count())
            .select_from(ClickEvent)
            .where(ClickEvent.short_code == short_code),
        )
        return result.scalar_one()

    async def clicks_by_day(self, short_code: str) -> list[tuple[date, int]]:
        """Return ``(day, count)`` pairs for ``short_code``, oldest day first.

        Grouping is done in SQL by casting the timestamp to a date.
        """
        day = cast(ClickEvent.clicked_at, Date).label("day")
        result = await self._session.execute(
            select(day, func.count().label("count"))
            .where(ClickEvent.short_code == short_code)
            .group_by(day)
            .order_by(day),
        )
        return [(row_day, row_count) for row_day, row_count in result.all()]

    async def top_referrers(
        self,
        short_code: str,
        limit: int,
    ) -> list[tuple[str, int]]:
        """Return the top ``limit`` referrers for ``short_code`` by click count.

        Rows with no referrer are excluded from the ranking.
        """
        result = await self._session.execute(
            select(ClickEvent.referrer, func.count().label("count"))
            .where(
                ClickEvent.short_code == short_code,
                ClickEvent.referrer.is_not(None),
            )
            .group_by(ClickEvent.referrer)
            .order_by(func.count().desc())
            .limit(limit),
        )
        return [(referrer, count) for referrer, count in result.all()]
