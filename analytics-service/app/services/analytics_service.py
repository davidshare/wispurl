"""Ingestion and aggregation business logic."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.anonymize import anonymize_ip
from app.config import AnalyticsSettings
from app.repositories.click_event_repository import ClickEventRepository
from app.schemas.event import RecordClickRequest
from app.schemas.stats import DailyClicks, ReferrerCount, StatsResponse


@dataclass(frozen=True)
class IngestResult:
    """Outcome of ingesting one click."""

    total: int
    crossed_milestones: list[int]


class AnalyticsService:
    """Coordinates click ingestion and stats aggregation."""

    def __init__(self, session: AsyncSession, settings: AnalyticsSettings) -> None:
        self._session = session
        self._settings = settings
        self._events = ClickEventRepository(session)

    async def ingest_click(
        self,
        payload: RecordClickRequest,
        *,
        milestones: list[int],
    ) -> IngestResult:
        """Persist one click (IP anonymized) and report any milestone crossing.

        The single source of truth for the click WRITE — both the HTTP ``/events``
        handler and the queue consumer call this, so the insert logic is never
        duplicated.

        Milestone detection compares the per-short_code total before and after this
        insert and reports any threshold in ``(before, after]``. This is exact only
        when ingestion is single-flight per short_code; the consumer therefore runs
        with ``prefetch=1`` so a threshold fires exactly once.
        """
        short_code = payload.short_code
        before = await self._events.count_total(short_code)
        await self._events.create(
            short_code=short_code,
            ip_address=anonymize_ip(payload.ip_address),
            referrer=payload.referrer,
            user_agent=payload.user_agent,
            clicked_at=payload.clicked_at,
        )
        await self._session.commit()
        after = before + 1
        crossed = [threshold for threshold in milestones if before < threshold <= after]
        return IngestResult(total=after, crossed_milestones=crossed)

    async def record_click(self, payload: RecordClickRequest) -> None:
        """Persist one click without milestone detection (HTTP ``/events`` path)."""
        await self.ingest_click(payload, milestones=[])

    async def get_stats(self, short_code: str) -> StatsResponse:
        """Aggregate and return stats for ``short_code`` (aggregates only).

        A code with no recorded clicks yields a valid response with a zero total and
        empty buckets, rather than a 404 — "no data yet" is a normal answer.
        """
        total = await self._events.count_total(short_code)
        by_day = await self._events.clicks_by_day(short_code)
        referrers = await self._events.top_referrers(
            short_code,
            self._settings.top_referrers_limit,
        )
        return StatsResponse(
            short_code=short_code,
            total_clicks=total,
            clicks_by_day=[
                DailyClicks(date=day, count=count) for day, count in by_day
            ],
            top_referrers=[
                ReferrerCount(referrer=referrer, count=count)
                for referrer, count in referrers
            ],
        )
