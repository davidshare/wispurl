"""Proxy routes for the QR Code service.

DECISION: ``/qr/*`` is PUBLIC. A QR code encodes nothing more than the already
public short URL, so gating it behind a token would add friction without protecting
anything — anyone with the short link can already visit it. Change this to a
protected route (add ``dependencies=[Depends(get_current_user_id)]``) if QR
generation later exposes private information.
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.config import get_settings
from app.proxy import proxy

router = APIRouter(tags=["qr"])


@router.get("/v1/qr/{path:path}")
async def proxy_qr(path: str, request: Request) -> StreamingResponse:
    """Forward ``GET /qr/<path>`` to the QR service; public (no token required)."""
    settings = get_settings()
    return await proxy(
        request,
        base_url=str(settings.qr_service_url),
        upstream_path=request.url.path,
    )
