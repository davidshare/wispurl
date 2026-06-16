from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Request, status
from fastapi.responses import RedirectResponse

from app.config import ShortenerSettings
from app.dependencies import SessionDep, SettingsDep
from app.services.analytics import ClickMetadata, log_click
from app.services.link_service import LinkService
from app.services.shortcode import validate_short_code_path

router = APIRouter(tags=["redirect"])


async def safe_log_click(
    *,
    short_code: str,
    metadata: ClickMetadata,
    settings: ShortenerSettings,
) -> None:
    try:
        await log_click(short_code=short_code, metadata=metadata, settings=settings)
    except Exception:
        return


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
        ip_address=request.client.host if request.client else None,
        referrer=request.headers.get("referer"),
        user_agent=request.headers.get("user-agent"),
    )
    background_tasks.add_task(
        safe_log_click,
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
