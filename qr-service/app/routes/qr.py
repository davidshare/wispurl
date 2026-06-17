"""QR image endpoint (``GET /qr/{short_code}``).

Public by design — a QR image just encodes the already-public short URL. The service
does NOT verify that the code exists: doing so would couple it to the Shortener/DB
and break its stateless, infinitely-scalable nature. It simply encodes
``PUBLIC_BASE_URL + short_code`` as a PNG.
"""

from __future__ import annotations

import io
import re
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from app.config import QrSettings, get_settings
from app.errors.exceptions import InvalidShortCodeError
from app.schemas.qr import QrQuery
from app.services.qr_generator import generate_qr_png

logger = structlog.get_logger()

router = APIRouter(tags=["qr"])

# Same slug charset and length bounds the Shortener accepts.
_SHORT_CODE_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


@router.get("/qr/{short_code}")
async def get_qr(
    short_code: str,
    query: Annotated[QrQuery, Query()],
    settings: Annotated[QrSettings, Depends(get_settings)],
) -> StreamingResponse:
    """Return a scannable PNG QR code for ``short_code``.

    Validates the code charset/length and the requested size (rejecting out-of-range
    sizes with 422) before doing any work — image generation is the main abuse
    surface, so all bounds are enforced first.
    """
    if not _SHORT_CODE_PATTERN.fullmatch(short_code):
        raise InvalidShortCodeError

    size = query.size if query.size is not None else settings.default_size_px
    if not settings.min_size_px <= size <= settings.max_size_px:
        raise InvalidShortCodeError

    target_url = f"{settings.public_base_url_str}/{short_code}"
    png = generate_qr_png(data=target_url, size_px=size)

    logger.info("qr_generated", short_code=short_code, size=size)
    return StreamingResponse(
        io.BytesIO(png),
        media_type="image/png",
        headers={"Cache-Control": f"public, max-age={settings.cache_ttl}"},
    )
