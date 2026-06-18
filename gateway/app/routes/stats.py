"""Protected proxy routes for the Analytics service's stats API.

``/stats/*`` requires a valid access token (verified locally). The path is
forwarded unchanged because the Analytics service exposes its routes under
``/stats`` too. The Analytics ingest endpoint (``POST /events``) is internal and is
NOT exposed through the gateway.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.config import get_settings
from app.proxy import proxy
from app.security.auth import get_current_user_id

router = APIRouter(tags=["stats"])

_PROXY_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]


@router.api_route(
    "/v1/stats/{path:path}",
    methods=_PROXY_METHODS,
    dependencies=[Depends(get_current_user_id)],
)
async def proxy_stats(path: str, request: Request) -> StreamingResponse:
    """Forward ``/stats/<path>`` to the Analytics service; token required."""
    settings = get_settings()
    return await proxy(
        request,
        base_url=str(settings.analytics_service_url),
        upstream_path=request.url.path,
    )
