"""Protected proxy routes for the Shortener service's link-management API.

Both ``/links`` and ``/links/<id>`` require a valid access token (verified locally
by :func:`app.security.auth.get_current_user_id`). The gateway forwards the full
path unchanged because the Shortener mounts these routes under ``/links`` too.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.config import get_settings
from app.proxy import proxy
from app.security.auth import get_current_user_id

router = APIRouter(tags=["links"])

_PROXY_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]


async def _forward_links(request: Request) -> StreamingResponse:
    """Forward the request to the Shortener, preserving the ``/links`` path."""
    settings = get_settings()
    return await proxy(
        request,
        base_url=str(settings.shortener_service_url),
        upstream_path=request.url.path,
    )


@router.api_route(
    "/links",
    methods=_PROXY_METHODS,
    dependencies=[Depends(get_current_user_id)],
)
async def proxy_links_root(request: Request) -> StreamingResponse:
    """Forward ``/links`` (list/create) to the Shortener; token required."""
    return await _forward_links(request)


@router.api_route(
    "/links/{path:path}",
    methods=_PROXY_METHODS,
    dependencies=[Depends(get_current_user_id)],
)
async def proxy_links_path(path: str, request: Request) -> StreamingResponse:
    """Forward ``/links/<path>`` (e.g. delete by id) to the Shortener; auth required."""
    return await _forward_links(request)
