"""Internal-caller authentication for ``POST /events``.

``/events`` is never exposed through the gateway and is reachable only on the
internal Docker network, but network isolation alone is not authentication: any
peer on that network could otherwise forge click data. Callers must therefore
present a shared secret in the ``X-Internal-Key`` header, compared in constant time.
"""

from __future__ import annotations

import hmac
from typing import Annotated

from fastapi import Depends, Header

from app.config import AnalyticsSettings, get_settings
from app.errors.exceptions import UnauthorizedError


async def require_internal_key(
    settings: Annotated[AnalyticsSettings, Depends(get_settings)],
    x_internal_key: Annotated[str | None, Header()] = None,
) -> None:
    """Reject the request with a generic 401 unless the internal key matches.

    Uses :func:`hmac.compare_digest` to avoid leaking the key via timing.
    """
    if x_internal_key is None or not hmac.compare_digest(
        x_internal_key,
        settings.internal_api_key,
    ):
        raise UnauthorizedError
