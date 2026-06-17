import logging
import sys
from typing import Any

import structlog

SECRET_KEYS = {
    "access_token",
    "authorization",
    "jwt_secret",
    "refresh_token",
    "token",
}


def _scrub_secrets(
    _logger: Any,
    _method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    for key in list(event_dict):
        if key.lower() in SECRET_KEYS:
            event_dict[key] = "[redacted]"
    return event_dict


def configure_logging(service_name: str, log_level: str = "INFO") -> None:
    """Configure JSON logs with request_id-friendly context binding."""

    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        _scrub_secrets,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.EventRenamer("message"),
    ]

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level.upper(),
        force=True,
    )

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(log_level.upper()),
        ),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    structlog.contextvars.bind_contextvars(service=service_name)


def bind_request_id(request_id: str | None) -> None:
    if request_id:
        structlog.contextvars.bind_contextvars(request_id=request_id)


def clear_request_context() -> None:
    structlog.contextvars.clear_contextvars()
