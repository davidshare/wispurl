"""Aggregated statistics endpoint (``GET /stats/{short_code}``).

Protected by access-token verification (AUTHZ option (a) — see
:mod:`app.security.auth`). Returns aggregates only.
"""

from __future__ import annotations

import re

from fastapi import APIRouter

from app.dependencies import CurrentUserIdDep, SessionDep, SettingsDep
from app.errors.exceptions import AnalyticsDomainError
from app.schemas.stats import StatsResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(tags=["stats"])

_SHORT_CODE_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,32}$")


class InvalidShortCodeError(AnalyticsDomainError):
    """Raised when a stats request carries a malformed short code."""

    status_code = 422
    client_message = "Invalid request"


@router.get("/stats/{short_code}", response_model=StatsResponse)
async def get_stats(
    short_code: str,
    _current_user_id: CurrentUserIdDep,
    session: SessionDep,
    settings: SettingsDep,
) -> StatsResponse:
    """Return total, by-day, and top-referrer aggregates for ``short_code``.

    The caller must present a valid access token. The short code is shape-validated
    before any query runs (cheap rejection of malformed input).
    """
    if not _SHORT_CODE_PATTERN.fullmatch(short_code):
        raise InvalidShortCodeError
    service = AnalyticsService(session, settings)
    return await service.get_stats(short_code)
