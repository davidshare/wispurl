"""Public proxy routes for the Auth service.

The ``/v1/auth/*`` endpoints are how clients obtain and rotate tokens (signup,
login, refresh, logout), so the gateway must NEVER require a token here — they are
deliberately public and pass straight through.
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.config import get_settings
from app.proxy import proxy

router = APIRouter(prefix="/v1/auth", tags=["auth"])

# Auth endpoints are not idempotent reads only; allow the full verb set so any
# future Auth route is forwarded faithfully without editing the gateway.
_PROXY_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]


@router.api_route("/{path:path}", methods=_PROXY_METHODS)
async def proxy_auth(path: str, request: Request) -> StreamingResponse:
    """Forward ``/v1/auth/<path>`` to the Auth service WITHOUT requiring a token.

    The full versioned path is forwarded unchanged (the Auth service also mounts
    its routes under ``/v1/auth``).
    """
    settings = get_settings()
    return await proxy(
        request,
        base_url=str(settings.auth_service_url),
        upstream_path=request.url.path,
    )
