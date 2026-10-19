from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from wispurl_metrics.business import AUTH_EVENTS

from app.dependencies import SessionDep, SettingsDep, local_abuse_guard
from app.errors.exceptions import (
    AuthDomainError,
    DuplicateUserError,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    TooManyRequestsError,
    WeakPasswordError,
    empty_response,
)
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

# Domain error -> bounded `result` label for wispurl_auth_events_total.
_RESULTS: dict[type[AuthDomainError], str] = {
    DuplicateUserError: "duplicate_email",
    WeakPasswordError: "weak_password",
    InvalidCredentialsError: "invalid_credentials",
    InactiveUserError: "inactive_user",
    InvalidRefreshTokenError: "invalid_token",
    TooManyRequestsError: "rate_limited",
}


def _record_failure(action: str, exc: AuthDomainError) -> None:
    AUTH_EVENTS.labels(action=action, result=_RESULTS.get(type(exc), "rejected")).inc()


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
    try:
        user = await service.signup(
            email=str(payload.email),
            password=payload.password.get_secret_value(),
        )
    except AuthDomainError as exc:
        _record_failure("signup", exc)
        raise
    AUTH_EVENTS.labels(action="signup", result="success").inc()
    return user


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
    try:
        tokens = await service.login(
            email=str(payload.email),
            password=payload.password.get_secret_value(),
        )
    except AuthDomainError as exc:
        _record_failure("login", exc)
        raise
    AUTH_EVENTS.labels(action="login", result="success").inc()
    return tokens


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
    try:
        tokens = await service.refresh(refresh_token=payload.refresh_token)
    except AuthDomainError as exc:
        _record_failure("refresh", exc)
        raise
    AUTH_EVENTS.labels(action="refresh", result="success").inc()
    return tokens


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
    try:
        await service.logout(refresh_token=payload.refresh_token)
    except AuthDomainError as exc:
        _record_failure("logout", exc)
        raise
    AUTH_EVENTS.labels(action="logout", result="success").inc()
    return empty_response()
