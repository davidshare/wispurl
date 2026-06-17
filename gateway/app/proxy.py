"""The forwarding engine.

The gateway owns no business logic; every matched route delegates to :func:`proxy`
to relay the incoming request to the correct internal service and stream the
upstream response back to the caller.

Design guarantees:
  * Hop-by-hop headers are stripped in BOTH directions (RFC 9110 §7.6.1).
  * Redirects are never followed server-side (the shared client is created with
    ``follow_redirects=False``), so a Shortener ``307`` is handed back to the end
    user's browser unchanged — status and ``Location`` intact.
  * The client's ``Authorization`` header is forwarded upstream verbatim so the
    backend can independently re-verify the token (defense in depth).
  * Identity-injection headers from the client (``X-User-Id``) are never relayed,
    and the gateway's own correlation id (``X-Request-ID``) replaces any inbound one.
  * Connection failures map to ``502`` and timeouts to ``504``; upstream internals
    never leak to the client.
"""

from __future__ import annotations

import httpx
from fastapi import Request
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask

from app.errors.exceptions import UpstreamTimeoutError, UpstreamUnavailableError

# Hop-by-hop headers describe a single transport connection, not the end-to-end
# message, and must not be forwarded by a proxy (RFC 9110 §7.6.1).
HOP_BY_HOP_HEADERS: frozenset[str] = frozenset(
    {
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailer",
        "transfer-encoding",
        "upgrade",
    },
)

# Inbound request headers we refuse to relay verbatim:
#   * host             -> httpx sets the correct Host for the upstream target.
#   * x-request-id     -> replaced by the gateway's own correlation id.
#   * x-user-id        -> trust-injection vector; identity comes only from the
#                         verified JWT, never from a client-supplied header.
#   * x-forwarded-for  -> the gateway is the trust boundary, so it sets this from
#                         the direct peer rather than trusting a client-supplied
#                         chain (which a caller could spoof to forge a source IP).
_DROP_REQUEST_HEADERS: frozenset[str] = HOP_BY_HOP_HEADERS | {
    "host",
    "x-request-id",
    "x-user-id",
    "x-forwarded-for",
}


def _filter_request_headers(request: Request, request_id: str) -> list[tuple[str, str]]:
    """Build the upstream request headers: drop unsafe ones, set our own metadata.

    Sets ``X-Request-ID`` to the gateway's correlation id and ``X-Forwarded-For`` to
    the direct peer's IP so downstream services (e.g. the click-logging path to
    Analytics) can attribute the real client rather than the gateway's own address.
    """
    headers = [
        (key, value)
        for key, value in request.headers.items()
        if key.lower() not in _DROP_REQUEST_HEADERS
    ]
    headers.append(("x-request-id", request_id))
    if request.client is not None:
        headers.append(("x-forwarded-for", request.client.host))
    return headers


def _filter_response_headers(response: httpx.Response) -> list[tuple[bytes, bytes]]:
    """Return the upstream response headers minus hop-by-hop headers.

    Encoded as raw ``(bytes, bytes)`` pairs so duplicate headers (e.g. multiple
    ``Set-Cookie``) are preserved faithfully when assigned to ``raw_headers``.
    """
    return [
        (key.encode("latin-1"), value.encode("latin-1"))
        for key, value in response.headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS
    ]


async def proxy(
    request: Request,
    *,
    base_url: str,
    upstream_path: str,
) -> StreamingResponse:
    """Forward ``request`` to ``base_url + upstream_path`` and stream the response.

    Args:
        request: The incoming client request. The shared ``httpx.AsyncClient`` and
            the per-request correlation id are read from its app/request state.
        base_url: The internal base URL of the target service (e.g.
            ``http://shortener-service:8000``).
        upstream_path: The path to request on the upstream, beginning with ``/``.
            The caller decides whether to keep or strip the gateway prefix.

    Returns:
        A ``StreamingResponse`` carrying the upstream status, body, and headers
        (minus hop-by-hop headers). The response body is streamed and the upstream
        connection is closed via a background task once the body is exhausted.

    Raises:
        UpstreamTimeoutError: The upstream did not respond within the timeout (504).
        UpstreamUnavailableError: The upstream could not be reached (502).
    """
    client: httpx.AsyncClient = request.app.state.http_client
    request_id: str = request.state.request_id

    target = f"{base_url.rstrip('/')}{upstream_path}"
    if request.url.query:
        target = f"{target}?{request.url.query}"

    # Buffer the (small) request body; the response is what we stream back.
    body = await request.body()
    upstream_request = client.build_request(
        method=request.method,
        url=target,
        headers=_filter_request_headers(request, request_id),
        content=body,
    )

    try:
        upstream_response = await client.send(upstream_request, stream=True)
    except httpx.TimeoutException as exc:
        raise UpstreamTimeoutError from exc
    except httpx.HTTPError as exc:
        # Connect errors, refused connections, protocol errors -> bad gateway.
        raise UpstreamUnavailableError from exc

    response = StreamingResponse(
        upstream_response.aiter_raw(),
        status_code=upstream_response.status_code,
        background=BackgroundTask(upstream_response.aclose),
    )
    # Replace the auto-generated headers wholesale so we relay exactly the upstream
    # set (sans hop-by-hop) — including the upstream Content-Type and Location, and
    # without the placeholder ``content-type: text/plain`` StreamingResponse adds.
    response.raw_headers = _filter_response_headers(upstream_response)
    return response
