"""Internal-caller authentication for ``POST /check``.

``/check`` is never exposed through the gateway and is reachable only on the
internal Docker network, but network isolation is not authentication: without a
credential, any peer could spoof ``user_id`` values to exhaust or bypass limits.
Callers must therefore present a shared secret in ``X-Internal-Key``, compared in
constant time.
"""

from __future__ import annotations

import hmac
from typing import Annotated

from fastapi import Depends, Header

from app.config import RateLimiterSettings, get_settings
from app.errors.exceptions import UnauthorizedError


async def require_internal_key(
    settings: Annotated[RateLimiterSettings, Depends(get_settings)],
    x_internal_key: Annotated[str | None, Header()] = None,
) -> None:
    """Reject the request with a generic 401 unless the internal key matches."""
    if x_internal_key is None or not hmac.compare_digest(
        x_internal_key,
        settings.internal_api_key,
    ):
        raise UnauthorizedError
