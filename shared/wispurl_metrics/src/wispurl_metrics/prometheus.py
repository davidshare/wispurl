import os
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
    multiprocess,
)

# Label for requests that matched no route (404s, scanners). Using the raw URL
# instead would create a new time series for every random path.
UNMATCHED_PATH = "<unmatched>"

# 1. Define metrics using the default global registry
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["service", "method", "path", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["service", "method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

# No path label: the route is only known after routing, but this gauge must go
# up before the request runs. livesum = sum across live Gunicorn workers.
REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "HTTP requests currently being processed",
    ["service", "method"],
    multiprocess_mode="livesum",
)


# 2. The reusable middleware class
class PrometheusMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, service_name: str):
        super().__init__(app)
        self.service_name = service_name

    async def dispatch(self, request: Request, call_next):
        method = request.method
        in_progress = REQUESTS_IN_PROGRESS.labels(
            service=self.service_name,
            method=method,
        )
        in_progress.inc()

        start = time.perf_counter()
        response = None

        try:
            response = await call_next(request)
            return response
        finally:
            duration = time.perf_counter() - start
            # Default to "500" if an exception occurred and no response was generated
            status = str(response.status_code) if response else "500"

            # Routing has run by now, so the route template (e.g. /links/{short_code})
            # is known. Labelling by template, not raw URL, keeps cardinality bounded.
            route = request.scope.get("route")
            path = getattr(route, "path", UNMATCHED_PATH)

            REQUEST_COUNT.labels(
                service=self.service_name,
                method=method,
                path=path,
                status=status,
            ).inc()

            REQUEST_LATENCY.labels(
                service=self.service_name,
                method=method,
                path=path,
            ).observe(duration)

            in_progress.dec()


# 3. The reusable metrics endpoint
def metrics_endpoint(request: Request) -> Response:
    # Under Gunicorn with several workers, each worker has its own counters.
    # With PROMETHEUS_MULTIPROC_DIR set, aggregate every worker's values so a
    # scrape sees the whole service, not whichever worker answered.
    if os.environ.get("PROMETHEUS_MULTIPROC_DIR"):
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
    else:
        registry = REGISTRY
    return Response(
        content=generate_latest(registry),
        media_type=CONTENT_TYPE_LATEST,
    )
