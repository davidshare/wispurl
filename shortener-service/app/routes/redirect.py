from __future__ import annotations

import httpx
import structlog
from fastapi import APIRouter, BackgroundTasks, Request, status
from fastapi.responses import RedirectResponse

from app.config import ShortenerSettings
from app.dependencies import SessionDep, SettingsDep
from app.services.analytics import ClickMetadata, log_click
from app.services.link_service import LinkService
from app.services.shortcode import validate_short_code_path
from shared.messaging import (
    ROUTING_KEY_LINK_CLICKED,
    EventPublisher,
    build_envelope,
)

logger = structlog.get_logger()

router = APIRouter(tags=["redirect"])


def _client_ip(request: Request) -> str | None:
    """Return the originating client IP.

    Prefers the first hop of ``X-Forwarded-For`` (set by the gateway, since the
    direct peer is the gateway itself) and falls back to the socket peer for direct
    requests. The raw IP is anonymized by the Analytics service before storage.
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None

# Open redirect to a user-supplied URL is INTENTIONAL here: this is a URL
# shortener, so redirecting the end user's browser to long_url is the product.
# It is kept safe by restricting long_url to http/https at creation time
# (see app/schemas/link.py), so the redirect can never deliver a
# javascript:/data:/file: payload. If a denylist or safe-browsing check is ever
# wanted, gate it at creation time, not here on the hot redirect path.
#
# SSRF note: this service only redirects the end user's browser; it NEVER fetches
# long_url server-side. If a future feature does fetch it (e.g. link previews,
# title scraping, favicon fetch), that fetch MUST guard against SSRF by blocking
# internal/link-local/metadata ranges (127.0.0.0/8, 169.254.0.0/16, 10/8,
# 172.16/12, 192.168/16, ::1, fc00::/7) and resolving DNS before connecting.


async def safe_log_click(
    *,
    client: httpx.AsyncClient,
    short_code: str,
    metadata: ClickMetadata,
    settings: ShortenerSettings,
) -> None:
    """Fail-open wrapper around :func:`log_click`.

    Runs in a background task after the redirect is sent. Any error (Analytics down,
    slow, or returning an error status) is logged as a warning and swallowed so the
    already-sent redirect is never affected.
    """
    try:
        await log_click(
            client=client,
            short_code=short_code,
            metadata=metadata,
            settings=settings,
        )
    except Exception as exc:
        logger.warning("click_log_failed", short_code=short_code, error=str(exc))


async def safe_publish_click(
    *,
    publisher: EventPublisher,
    short_code: str,
    metadata: ClickMetadata,
    request_id: str | None,
) -> None:
    """Fail-open wrapper that publishes a ``link.clicked`` event.

    Runs in a background task after the redirect is sent. A broker outage (or any
    publish error) is logged and swallowed: the click may be dropped — the
    documented tradeoff — but the already-sent redirect is never affected.
    """
    try:
        envelope = build_envelope(
            event=ROUTING_KEY_LINK_CLICKED,
            data={
                "short_code": short_code,
                "ip_address": metadata.ip_address,
                "referrer": metadata.referrer,
                "user_agent": metadata.user_agent,
            },
            request_id=request_id,
        )
        await publisher.publish(envelope, routing_key=ROUTING_KEY_LINK_CLICKED)
    except Exception as exc:
        logger.warning("click_publish_failed", short_code=short_code, error=str(exc))


@router.get("/{short_code}", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def redirect_short_code(
    short_code: str,
    request: Request,
    background_tasks: BackgroundTasks,
    session: SessionDep,
    settings: SettingsDep,
) -> RedirectResponse:
    validated_code = validate_short_code_path(short_code)
    service = LinkService(session, settings)
    link = await service.resolve_link(short_code=validated_code)
    metadata = ClickMetadata(
        ip_address=_client_ip(request),
        referrer=request.headers.get("referer"),
        user_agent=request.headers.get("user-agent"),
    )
    request_id = request.headers.get("x-request-id")

    # Preferred path: publish a "link.clicked" event to RabbitMQ (decoupled).
    publisher: EventPublisher | None = getattr(
        request.app.state,
        "event_publisher",
        None,
    )
    if settings.events_publish_enabled and publisher is not None:
        background_tasks.add_task(
            safe_publish_click,
            publisher=publisher,
            short_code=validated_code,
            metadata=metadata,
            request_id=request_id,
        )

    # Optional legacy fallback: direct HTTP POST to Analytics (off by default).
    if settings.analytics_http_fallback:
        background_tasks.add_task(
            safe_log_click,
            client=request.app.state.http_client,
            short_code=validated_code,
            metadata=metadata,
            settings=settings,
        )

    response = RedirectResponse(
        url=link.long_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )
    response.headers["Cache-Control"] = "no-store"
    return response
