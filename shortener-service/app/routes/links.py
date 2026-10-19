from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Request, Response, status
from wispurl_metrics.business import (
    LINK_CREATE_REJECTIONS,
    LINKS_CREATED,
    LINKS_DELETED,
)

from app.dependencies import CurrentUserIdDep, SessionDep, SettingsDep
from app.errors.exceptions import (
    DuplicateShortCodeError,
    InvalidSlugError,
    LinkNotFoundError,
    RateLimitExceededError,
    ShortCodeExhaustedError,
    empty_response,
)
from app.schemas.link import CreateLinkRequest, LinkListResponse, LinkResponse
from app.services.link_service import LinkService

router = APIRouter(prefix="/v1/links", tags=["links"])

# Domain error -> bounded `reason` label for wispurl_link_create_rejections_total.
_REJECTIONS = {
    RateLimitExceededError: "rate_limited",
    DuplicateShortCodeError: "duplicate_slug",
    InvalidSlugError: "invalid_slug",
    ShortCodeExhaustedError: "exhausted",
}


@router.post("", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
async def create_link(
    payload: CreateLinkRequest,
    request: Request,
    current_user_id: CurrentUserIdDep,
    session: SessionDep,
    settings: SettingsDep,
) -> LinkResponse:
    service = LinkService(session, settings)
    try:
        link = await service.create_link(
            client=request.app.state.http_client,
            user_id=current_user_id,
            long_url=str(payload.long_url),
            custom_slug=payload.custom_slug,
            expires_at=payload.expires_at,
        )
    except tuple(_REJECTIONS) as exc:
        LINK_CREATE_REJECTIONS.labels(reason=_REJECTIONS[type(exc)]).inc()
        raise
    LINKS_CREATED.labels(
        slug="custom" if payload.custom_slug else "generated",
        expiry="yes" if payload.expires_at else "no",
    ).inc()
    return link


@router.get("", response_model=LinkListResponse)
async def list_links(
    current_user_id: CurrentUserIdDep,
    session: SessionDep,
    settings: SettingsDep,
    limit: Annotated[int | None, Query(ge=1)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> LinkListResponse:
    service = LinkService(session, settings)
    actual_limit = min(limit or settings.default_page_limit, settings.max_page_limit)
    return await service.list_links(
        user_id=current_user_id,
        limit=actual_limit,
        offset=offset,
    )


@router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(
    link_id: UUID,
    current_user_id: CurrentUserIdDep,
    session: SessionDep,
    settings: SettingsDep,
) -> Response:
    service = LinkService(session, settings)
    try:
        await service.delete_link(user_id=current_user_id, link_id=link_id)
    except LinkNotFoundError:
        LINKS_DELETED.labels(result="not_found").inc()
        raise
    LINKS_DELETED.labels(result="deleted").inc()
    return empty_response()
