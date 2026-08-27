import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST, REGISTRY

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

REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "HTTP requests currently being processed",
    ["service", "method", "path"],
)


# 2. The reusable middleware class
class PrometheusMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, service_name: str):
        super().__init__(app)
        self.service_name = service_name

    async def dispatch(self, request: Request, call_next):
        method = request.method

        # Prevent cardinality explosion by using the route template (e.g., /users/{id})
        # Falls back to raw url.path for 404s or unmatched routes
        route = request.scope.get("route")
        path = route.path if route else request.url.path

        REQUESTS_IN_PROGRESS.labels(
            service=self.service_name,
            method=method,
            path=path,
        ).inc()

        start = time.perf_counter()
        response = None

        try:
            response = await call_next(request)
            return response
        finally:
            duration = time.perf_counter() - start
            # Default to "500" if an exception occurred and no response was generated
            status = str(response.status_code) if response else "500"

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

            REQUESTS_IN_PROGRESS.labels(
                service=self.service_name,
                method=method,
                path=path,
            ).dec()


# 3. The reusable metrics endpoint
def metrics_endpoint(request: Request) -> Response:
    return Response(
        content=generate_latest(REGISTRY),
        media_type=CONTENT_TYPE_LATEST,
    )
