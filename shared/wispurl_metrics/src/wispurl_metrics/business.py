"""Business and messaging metrics for WispURL.

HTTP metrics (prometheus.py) say how the services behave; these say what the
product is doing: signups, links, redirects, clicks, notifications, and how the
event pipeline between services is coping.

Rules for every metric here:
- labels only take values from small, fixed sets (never user IDs, emails, short
  codes or URLs);
- every metric has at least one label, so a service that imports this module
  but never uses a metric doesn't export meaningless zero series.
"""

from prometheus_client import Counter, Histogram, start_http_server

# --- Accounts (auth-service) -------------------------------------------------

AUTH_EVENTS = Counter(
    "wispurl_auth_events_total",
    "Authentication requests by action and outcome",
    ["action", "result"],  # action: signup|login|refresh|logout
)

# --- Links (shortener-service) -----------------------------------------------

LINKS_CREATED = Counter(
    "wispurl_links_created_total",
    "Short links created",
    ["slug", "expiry"],  # slug: custom|generated, expiry: yes|no
)

LINK_CREATE_REJECTIONS = Counter(
    "wispurl_link_create_rejections_total",
    "Link creations refused, by reason",
    ["reason"],  # rate_limited|duplicate_slug|invalid_slug|exhausted
)

LINKS_DELETED = Counter(
    "wispurl_links_deleted_total",
    "Owner requests to delete a link",
    ["result"],  # deleted|not_found
)

REDIRECTS = Counter(
    "wispurl_redirects_total",
    "Short-link lookups on the redirect path, by outcome",
    ["result"],  # found|not_found|inactive|expired
)

RATE_LIMITER_UNAVAILABLE = Counter(
    "wispurl_rate_limiter_unavailable_total",
    "Rate-limit checks that failed, and what the shortener did instead",
    ["fallback"],  # allowed (fail-open)|denied (fail-closed)
)

# --- Rate limiting (rate-limiter-service) ------------------------------------

RATE_LIMIT_DECISIONS = Counter(
    "wispurl_rate_limit_decisions_total",
    "Rate-limit decisions by action",
    ["action", "decision"],  # decision: allowed|denied
)

# --- QR codes (qr-service) ---------------------------------------------------

QR_CODES_GENERATED = Counter(
    "wispurl_qr_codes_generated_total",
    "QR code images generated, by size band",
    ["size"],  # small (<=256px)|medium (<=512px)|large
)

# --- Analytics (analytics-service and its consumer) --------------------------

CLICKS_RECORDED = Counter(
    "wispurl_clicks_recorded_total",
    "Clicks written to the analytics store, by ingestion path",
    ["source"],  # queue|http
)

MILESTONES_REACHED = Counter(
    "wispurl_link_milestones_total",
    "Links that crossed a click milestone",
    ["threshold"],  # one of the configured MILESTONES values
)

# --- Expiry (cleanup-service) ------------------------------------------------

LINKS_EXPIRED = Counter(
    "wispurl_links_expired_total",
    "Links deactivated because they passed their expiry time",
    ["source"],  # cleanup
)

CLEANUP_SWEEP_SECONDS = Histogram(
    "wispurl_cleanup_sweep_seconds",
    "Duration of one expiry sweep, by outcome",
    ["outcome"],  # empty|deactivated|error
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0),
)

# --- Notifications (notification-service) ------------------------------------

NOTIFICATIONS = Counter(
    "wispurl_notifications_total",
    "Notifications handled, by event type, channel and outcome",
    ["type", "channel", "result"],  # type: link_expired|milestone|unknown
)

# --- Event pipeline (shared messaging module, every producer and consumer) ---

MESSAGES_PUBLISHED = Counter(
    "wispurl_messages_published_total",
    "Events published to RabbitMQ, by routing key and outcome",
    ["routing_key", "result"],  # result: ok|error
)

MESSAGES_PROCESSED = Counter(
    "wispurl_messages_processed_total",
    "Events taken off a queue, by queue and what happened to them",
    ["queue", "result"],  # ack|retry|dead_letter|malformed
)

MESSAGE_PROCESSING_SECONDS = Histogram(
    "wispurl_message_processing_seconds",
    "Time spent handling one event, by queue",
    ["queue"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)


def qr_size_band(size_px: int) -> str:
    """Map a pixel size to a bounded label value."""
    if size_px <= 256:
        return "small"
    if size_px <= 512:
        return "medium"
    return "large"


def start_metrics_server(port: int = 8000) -> None:
    """Serve /metrics from a single-process worker (no web framework needed).

    For Gunicorn services use metrics_endpoint() instead: this exposes only the
    calling process's metrics.
    """
    start_http_server(port)
