from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.dependencies import SessionDep, SettingsDep, local_abuse_guard
from app.errors.exceptions import empty_response
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    PublicUser,
    RefreshRequest,
    SignupRequest,
)
from app.schemas.token import TokenPair
from app.services.auth_service import AuthService

router = APIRouter(prefix="/v1/auth", tags=["auth"])

AbuseGuard = Annotated[None, Depends(local_abuse_guard)]


@router.post(
    "/signup",
    response_model=PublicUser,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(local_abuse_guard)],
)
async def signup(
    payload: SignupRequest,
    session: SessionDep,
    settings: SettingsDep,
) -> PublicUser:
    service = AuthService(session, settings)
    return await service.signup(
        email=str(payload.email),
        password=payload.password.get_secret_value(),
    )


@router.post(
    "/login",
    response_model=TokenPair,
    dependencies=[Depends(local_abuse_guard)],
)
async def login(
    payload: LoginRequest,
    session: SessionDep,
    settings: SettingsDep,
) -> TokenPair:
    service = AuthService(session, settings)
    return await service.login(
        email=str(payload.email),
        password=payload.password.get_secret_value(),
    )


@router.post(
    "/refresh",
    response_model=TokenPair,
    dependencies=[Depends(local_abuse_guard)],
)
async def refresh(
    payload: RefreshRequest,
    session: SessionDep,
    settings: SettingsDep,
) -> TokenPair:
    service = AuthService(session, settings)
    return await service.refresh(refresh_token=payload.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(local_abuse_guard)],
)
async def logout(
    payload: LogoutRequest,
    session: SessionDep,
    settings: SettingsDep,
) -> Response:
    service = AuthService(session, settings)
    await service.logout(refresh_token=payload.refresh_token)
    return empty_response()
