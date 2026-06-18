from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Request, Response, status

from app.dependencies import CurrentUserIdDep, SessionDep, SettingsDep
from app.errors.exceptions import empty_response
from app.schemas.link import CreateLinkRequest, LinkListResponse, LinkResponse
from app.services.link_service import LinkService

router = APIRouter(prefix="/v1/links", tags=["links"])


@router.post("", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
async def create_link(
    payload: CreateLinkRequest,
    request: Request,
    current_user_id: CurrentUserIdDep,
    session: SessionDep,
    settings: SettingsDep,
) -> LinkResponse:
    service = LinkService(session, settings)
    return await service.create_link(
        client=request.app.state.http_client,
        user_id=current_user_id,
        long_url=str(payload.long_url),
        custom_slug=payload.custom_slug,
        expires_at=payload.expires_at,
    )


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
    await service.delete_link(user_id=current_user_id, link_id=link_id)
    return empty_response()
