"""Internal click-ingestion endpoint (``POST /events``).

Gated by the internal shared key (:func:`app.security.internal.require_internal_key`)
and never exposed through the gateway. Accepts one click and returns ``202 Accepted``.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status

from app.dependencies import SessionDep, SettingsDep
from app.schemas.event import RecordClickRequest
from app.security.internal import require_internal_key
from app.services.analytics_service import AnalyticsService

router = APIRouter(tags=["events"])


@router.post(
    "/events",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_internal_key)],
)
async def record_event(
    payload: RecordClickRequest,
    session: SessionDep,
    settings: SettingsDep,
) -> Response:
    """Record a single click event; requires a valid ``X-Internal-Key``."""
    service = AnalyticsService(session, settings)
    await service.record_click(payload)
    return Response(status_code=status.HTTP_202_ACCEPTED)
