"""Response schemas for aggregated statistics (``GET /stats/{short_code}``).

These expose ONLY aggregates — totals, per-day counts, top referrers — never raw
per-visitor rows or stored IP values.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class DailyClicks(BaseModel):
    """Click count for a single calendar day (UTC)."""

    date: date
    count: int


class ReferrerCount(BaseModel):
    """Click count attributed to a single referrer."""

    referrer: str
    count: int


class StatsResponse(BaseModel):
    """Aggregated statistics for one short code."""

    short_code: str
    total_clicks: int
    clicks_by_day: list[DailyClicks]
    top_referrers: list[ReferrerCount]
