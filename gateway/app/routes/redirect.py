"""Public catch-all redirect route.

The Shortener owns a BARE top-level path ``GET /{short_code}`` with no prefix, so
the gateway treats any unmatched single-segment top-level GET as a short code and
forwards it to the Shortener. This router MUST be included LAST in
:mod:`app.main`, after every prefixed route, or it will swallow real routes.

The short code is validated cheaply at the gateway before forwarding: it must be a
single path segment matching the slug charset and must not equal a reserved prefix.
Anything else is rejected with a generic 404 — junk is never forwarded upstream.
"""

from __future__ import annotations

import re

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.config import get_settings
from app.errors.exceptions import NotFoundError
from app.proxy import proxy

router = APIRouter(tags=["redirect"])

# A single path segment of the slug charset. Because the param is ``{short_code}``
# (not ``{short_code:path}``), any value containing ``/`` simply fails to match the
# route and FastAPI returns 404 — multi-segment junk never reaches this handler.
_SHORT_CODE_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


@router.get("/{short_code}", status_code=307)
async def proxy_redirect(short_code: str, request: Request) -> StreamingResponse:
    """Forward ``GET /<short_code>`` to the Shortener for redirect resolution.

    The Shortener responds with a ``307`` whose ``Location`` is the long URL; the
    shared httpx client uses ``follow_redirects=False`` and the proxy relays that
    ``307`` unchanged, so the END USER's browser follows it — the gateway never does.
    """
    settings = get_settings()
    if (
        not _SHORT_CODE_PATTERN.fullmatch(short_code)
        or short_code.casefold() in settings.reserved_prefixes
    ):
        raise NotFoundError
    return await proxy(
        request,
        base_url=str(settings.shortener_service_url),
        upstream_path=f"/{short_code}",
    )
