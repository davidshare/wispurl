"""WispURL metrics: HTTP RED metrics (prometheus.py) and business metrics (business.py).

The HTTP pieces need Starlette, which the queue workers don't install, so they're
loaded only when first used. Workers can import wispurl_metrics.business alone.
"""

from typing import Any

__all__ = [
    "REQUEST_COUNT",
    "REQUEST_LATENCY",
    "REQUESTS_IN_PROGRESS",
    "PrometheusMiddleware",
    "metrics_endpoint",
]


def __getattr__(name: str) -> Any:
    if name in __all__:
        from . import prometheus

        return getattr(prometheus, name)
    raise AttributeError(f"module 'wispurl_metrics' has no attribute {name!r}")
