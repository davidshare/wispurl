#!/usr/bin/env python3
"""Generate WispURL's Grafana dashboards as JSON.

Panels and conventions are defined once here; every dashboard is built from them.
Run after changing anything, and commit both this file and the generated JSON:

    python3 observability/grafana/generate_dashboards.py

Grafana loads observability/grafana/dashboards/<folder>/*.json (one Grafana folder
per subdirectory) through the provider in provisioning/dashboards/dashboards.yaml.
Standard library only.
"""

from __future__ import annotations

import json
import pathlib
import shutil

OUT = pathlib.Path(__file__).resolve().parent / "dashboards"

PROM = {"type": "prometheus", "uid": "prometheus"}
LOKI = {"type": "loki", "uid": "loki"}
TEMPO = {"type": "tempo", "uid": "tempo"}

RI = "$__rate_interval"  # range for rate()/histogram_quantile() in time series
RANGE = "$__range"  # range for "total over the selected time range" stats


# =============================================================================
# Panel builders
# =============================================================================


def _target(expr: str, legend: str = "", ref: str = "A", instant: bool = False, fmt: str | None = None) -> dict:
    t = {"refId": ref, "datasource": PROM, "expr": expr, "legendFormat": legend, "range": not instant, "instant": instant}
    if fmt:
        t["format"] = fmt
    return t


def _targets(queries: list[tuple[str, str]], instant: bool = False, fmt: str | None = None) -> list[dict]:
    return [_target(q, legend, chr(65 + i), instant, fmt) for i, (q, legend) in enumerate(queries)]


def _thresholds(steps: list[tuple[float | None, str]]) -> dict:
    return {"mode": "absolute", "steps": [{"value": v, "color": c} for v, c in steps]}


GOOD_LOW = [(None, "green")]  # neutral: always green


def timeseries(
    title: str,
    queries: list[tuple[str, str]],
    unit: str = "short",
    desc: str = "",
    stack: bool = False,
    min_: float | None = 0,
    max_: float | None = None,
    thresholds: list | None = None,
    bars: bool = False,
) -> dict:
    defaults: dict = {
        "unit": unit,
        "custom": {
            "drawStyle": "bars" if bars else "line",
            "lineWidth": 1,
            "fillOpacity": 60 if bars else 12,
            "showPoints": "never",
            "stacking": {"mode": "normal" if stack else "none", "group": "A"},
            "spanNulls": True,
        },
    }
    if min_ is not None:
        defaults["min"] = min_
    if max_ is not None:
        defaults["max"] = max_
    if thresholds:
        defaults["thresholds"] = _thresholds(thresholds)
        defaults["custom"]["thresholdsStyle"] = {"mode": "dashed"}
    return {
        "type": "timeseries",
        "title": title,
        "description": desc,
        "datasource": PROM,
        "fieldConfig": {"defaults": defaults, "overrides": []},
        "options": {
            "legend": {"displayMode": "table", "placement": "bottom", "calcs": ["mean", "max", "lastNotNull"]},
            "tooltip": {"mode": "multi", "sort": "desc"},
        },
        "targets": _targets(queries),
    }


def stat(
    title: str,
    expr: str,
    unit: str = "short",
    desc: str = "",
    thresholds: list | None = None,
    decimals: int | None = None,
    links: list | None = None,
    graph: bool = False,
) -> dict:
    defaults: dict = {"unit": unit, "thresholds": _thresholds(thresholds or GOOD_LOW), "color": {"mode": "thresholds"}}
    if decimals is not None:
        defaults["decimals"] = decimals
    if links:
        defaults["links"] = links
    return {
        "type": "stat",
        "title": title,
        "description": desc,
        "datasource": PROM,
        "fieldConfig": {"defaults": defaults, "overrides": []},
        "options": {
            "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
            "colorMode": "background" if thresholds else "value",
            "graphMode": "area" if graph else "none",
            "textMode": "auto",
            "justifyMode": "center",
        },
        "targets": [_target(expr, "", "A", instant=not graph)],
    }


def gauge(title: str, expr: str, unit: str = "percentunit", desc: str = "", thresholds: list | None = None, max_: float = 1) -> dict:
    return {
        "type": "gauge",
        "title": title,
        "description": desc,
        "datasource": PROM,
        "fieldConfig": {
            "defaults": {
                "unit": unit,
                "min": 0,
                "max": max_,
                "thresholds": _thresholds(thresholds or [(None, "green"), (0.75, "orange"), (0.9, "red")]),
            },
            "overrides": [],
        },
        "options": {"reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False}, "showThresholdMarkers": True},
        "targets": [_target(expr, "", "A", instant=True)],
    }


def table(
    title: str,
    queries: list[tuple[str, str]],
    join_on: str,
    columns: dict[str, tuple[str, str]],
    desc: str = "",
    links: dict[str, list] | None = None,
    thresholds: dict[str, list] | None = None,
    extra_fields: tuple[str, ...] = (),
) -> dict:
    """An instant-query table: one row per `join_on` value, one column per query.

    columns maps "Value #A" style field names to (display name, unit).
    """
    overrides = []
    for field, (name, unit) in columns.items():
        props = [{"id": "displayName", "value": name}, {"id": "unit", "value": unit}]
        if thresholds and field in thresholds:
            props += [
                {"id": "thresholds", "value": _thresholds(thresholds[field])},
                {"id": "custom.cellOptions", "value": {"type": "color-text"}},
            ]
        overrides.append({"matcher": {"id": "byName", "options": field}, "properties": props})
    for field, field_links in (links or {}).items():
        overrides.append({"matcher": {"id": "byName", "options": field}, "properties": [{"id": "links", "value": field_links}]})
    keep = {join_on: False, **{f: False for f in extra_fields}, **{f: False for f in columns}}
    return {
        "type": "table",
        "title": title,
        "description": desc,
        "datasource": PROM,
        "fieldConfig": {"defaults": {"custom": {"align": "auto"}}, "overrides": overrides},
        "options": {"showHeader": True, "sortBy": [{"displayName": columns[next(iter(columns))][0], "desc": True}]},
        "targets": _targets(queries, instant=True, fmt="table"),
        "transformations": [
            {"id": "merge", "options": {}},
            {"id": "organize", "options": {"excludeByName": {"Time": True}, "indexByName": {}, "renameByName": {}}},
            {"id": "filterFieldsByName", "options": {"include": {"names": list(keep)}}},
        ],
    }


def heatmap(title: str, expr: str, unit: str = "s", desc: str = "") -> dict:
    return {
        "type": "heatmap",
        "title": title,
        "description": desc,
        "datasource": PROM,
        "fieldConfig": {"defaults": {"unit": unit}, "overrides": []},
        "options": {
            "calculate": False,
            "yAxis": {"unit": unit},
            "color": {"mode": "scheme", "scheme": "Oranges", "steps": 64},
            "cellGap": 1,
            "tooltip": {"mode": "single", "yHistogram": True},
        },
        "targets": [_target(expr, "{{le}}", "A", fmt="heatmap")],
    }


def logs(title: str, expr: str, desc: str = "") -> dict:
    return {
        "type": "logs",
        "title": title,
        "description": desc,
        "datasource": LOKI,
        "options": {"showTime": True, "wrapLogMessage": True, "sortOrder": "Descending", "enableLogDetails": True, "prettifyLogMessage": False},
        "targets": [{"refId": "A", "datasource": LOKI, "expr": expr, "queryType": "range"}],
    }


def log_volume(title: str, expr: str, legend: str, desc: str = "") -> dict:
    p = timeseries(title, [], "short", desc, stack=True, bars=True)
    p["datasource"] = LOKI
    p["targets"] = [{"refId": "A", "datasource": LOKI, "expr": expr, "legendFormat": legend, "queryType": "range"}]
    return p


def traces(title: str, traceql: str, desc: str = "") -> dict:
    return {
        "type": "table",
        "title": title,
        "description": desc,
        "datasource": TEMPO,
        "targets": [{"refId": "A", "datasource": TEMPO, "queryType": "traceql", "query": traceql, "limit": 20, "tableType": "traces"}],
    }


def text(title: str, markdown: str) -> dict:
    return {"type": "text", "title": title, "options": {"mode": "markdown", "content": markdown}}


def link_to(dashboard_uid: str, title: str, var: str | None = None, value: str = "${__value.raw}") -> dict:
    url = f"/d/{dashboard_uid}?${{__url_time_range}}"
    if var:
        url += f"&var-{var}={value}"
    return {"title": title, "url": url}


# =============================================================================
# Layout: rows of panels on Grafana's 24-column grid
# =============================================================================


class Layout:
    def __init__(self) -> None:
        self.panels: list[dict] = []
        self.y = 0
        self._next_id = 1

    def row(self, title: str, collapsed: bool = False) -> None:
        self.panels.append({"id": self._id(), "type": "row", "title": title, "collapsed": collapsed, "gridPos": {"x": 0, "y": self.y, "w": 24, "h": 1}, "panels": []})
        self.y += 1

    def add(self, panels: list[tuple[dict, int]], height: int = 8) -> None:
        """Place panels left to right; widths must add up to at most 24."""
        x = 0
        for panel, width in panels:
            panel = dict(panel)
            panel["id"] = self._id()
            panel["gridPos"] = {"x": x, "y": self.y, "w": width, "h": height}
            self.panels.append(panel)
            x += width
        self.y += height

    def _id(self) -> int:
        self._next_id += 1
        return self._next_id - 1


# =============================================================================
# Variables and dashboard wrapper
# =============================================================================


def query_var(name: str, label: str, query: str, multi: bool = False, include_all: bool = False, regex: str = "", ds: dict = PROM) -> dict:
    v = {
        "name": name,
        "label": label,
        "type": "query",
        "datasource": ds,
        "query": {"query": query, "refId": name, "qryType": 1},
        "definition": query,
        "multi": multi,
        "includeAll": include_all,
        "refresh": 2,
        "sort": 1,
        "regex": regex,
    }
    if include_all:
        v["allValue"] = ".*"
        v["current"] = {"text": "All", "value": "$__all"}
    return v


def custom_var(name: str, label: str, values: list[str], multi: bool = True, include_all: bool = True) -> dict:
    v = {
        "name": name,
        "label": label,
        "type": "custom",
        "query": ",".join(values),
        "options": [{"text": x, "value": x, "selected": False} for x in values],
        "multi": multi,
        "includeAll": include_all,
    }
    if include_all:
        v["allValue"] = ".*"
        v["current"] = {"text": "All", "value": "$__all"}
    return v


FOLDERS = {"overview": "Overview", "applications": "Applications", "infrastructure": "Infrastructure", "observability": "Observability"}


def dashboard(uid: str, title: str, folder: str, desc: str, layout: Layout, variables: list | None = None, time: str = "now-6h") -> tuple[str, str, dict]:
    links = [
        {"title": "All WispURL dashboards", "type": "dashboards", "tags": ["wispurl"], "asDropdown": True, "includeVars": False, "keepTime": True},
        {"title": FOLDERS[folder], "type": "dashboards", "tags": [f"wispurl-{folder}"], "asDropdown": True, "includeVars": False, "keepTime": True},
    ]
    return folder, uid, {
        "uid": uid,
        "title": title,
        "description": desc,
        "tags": ["wispurl", f"wispurl-{folder}"],
        "editable": False,
        "graphTooltip": 1,  # shared crosshair across panels
        "schemaVersion": 41,
        "time": {"from": time, "to": "now"},
        "refresh": "30s",
        "links": links,
        "templating": {"list": variables or []},
        "panels": layout.panels,
    }


# =============================================================================
# Shared query fragments
# =============================================================================

UP_APPS = 'up{job="docker-compose-services"}'
GW = 'service="gateway"'
FAILED = 'status=~"5.."'
WORKERS = "analytics-consumer-service|cleanup-service|notification-service"

ERR_THRESH = [(None, "green"), (0.01, "orange"), (0.05, "red")]
LAT_THRESH = [(None, "green"), (0.5, "orange"), (1, "red")]
ZERO_GOOD = [(None, "green"), (1, "red")]


def err_ratio(sel: str, by: str = "") -> str:
    group = f" by ({by})" if by else ""
    return f"(sum{group} (rate(http_requests_total{{{sel},{FAILED}}}[{RI}])) or sum{group} (rate(http_requests_total{{{sel}}}[{RI}])) * 0) / sum{group} (rate(http_requests_total{{{sel}}}[{RI}]))"


def quantile(q: float, metric: str, sel: str, by: str = "") -> str:
    group = f"{by}, le" if by else "le"
    return f"histogram_quantile({q}, sum by ({group}) (rate({metric}_bucket{{{sel}}}[{RI}])))"


def total(metric: str, sel: str = "") -> str:
    return f"sum(increase({metric}{{{sel}}}[{RANGE}])) or vector(0)"


# =============================================================================
# Dashboards
# =============================================================================


def overview() -> tuple:
    L = Layout()
    L.row("Health right now")
    L.add([
        (stat("Services up", f"sum({UP_APPS})", desc="App containers whose /metrics answered the last scrape."), 4),
        (stat("Services missing", f"count(count by (compose_service) (max_over_time({UP_APPS}[1h])) unless count by (compose_service) ({UP_APPS})) or vector(0)",
              desc="Services seen in the last hour that have no running container now (the ServiceDisappeared alert).", thresholds=ZERO_GOOD), 4),
        (stat("Firing alerts", 'count(ALERTS{alertstate="firing"}) or vector(0)', thresholds=ZERO_GOOD,
              links=[link_to("wispurl-alerting", "Open the Alerting dashboard")]), 4),
        (stat("Gateway requests/s", f"sum(rate(http_requests_total{{{GW}}}[{RI}]))", "reqps", graph=True), 3),
        (stat("Gateway 5xx ratio", err_ratio(GW), "percentunit", thresholds=ERR_THRESH, decimals=2), 3),
        (stat("Gateway p95 latency", quantile(0.95, "http_request_duration_seconds", GW), "s", thresholds=LAT_THRESH), 3),
        (stat("Dead-letter queue", 'sum(rabbitmq_detailed_queue_messages{queue="events.dlq"}) or vector(0)', thresholds=ZERO_GOOD,
              desc="Events that failed every retry. Each one is a lost click or notification.",
              links=[link_to("wispurl-workers", "Open Workers & Messaging")]), 3),
    ], height=5)

    L.row("Services")
    up_by_service = f'label_replace(sum by (compose_service) ({UP_APPS}), "service", "$1", "compose_service", "(.+)")'
    L.add([(table(
        "Service health",
        [
            (f"sum by (service) ({up_by_service})", ""),
            (f"sum by (service) (rate(http_requests_total[{RI}]))", ""),
            (err_ratio('service!=""', "service"), ""),
            (quantile(0.95, "http_request_duration_seconds", 'service!=""', "service"), ""),
        ],
        join_on="service",
        columns={"Value #A": ("Instances up", "short"), "Value #B": ("Requests/s", "reqps"), "Value #C": ("5xx ratio", "percentunit"), "Value #D": ("p95 latency", "s")},
        desc="Click a service to open its detail page. Workers have no HTTP columns; open them in Workers & Messaging.",
        links={"service": [link_to("wispurl-service", "Service detail for ${__value.raw}", "service"), link_to("wispurl-workers", "Workers & Messaging", "worker")]},
        thresholds={"Value #C": ERR_THRESH, "Value #D": LAT_THRESH},
    ), 24)], height=9)
    L.add([
        (timeseries("Requests per second by service", [(f"sum by (service) (rate(http_requests_total[{RI}]))", "{{service}}")], "reqps"), 8),
        (timeseries("5xx ratio by service", [(err_ratio('service!=""', "service"), "{{service}}")], "percentunit", thresholds=ERR_THRESH), 8),
        (timeseries("p95 latency by service", [(quantile(0.95, "http_request_duration_seconds", 'service!=""', "service"), "{{service}}")], "s", thresholds=LAT_THRESH), 8),
    ])

    L.row("Business over the selected time range")
    biz = lambda title, expr: (stat(title, expr, links=[link_to("wispurl-business", "Open the Business dashboard")]), 4)  # noqa: E731
    L.add([
        biz("New accounts", total("wispurl_auth_events_total", 'action="signup",result="success"')),
        biz("Links created", total("wispurl_links_created_total")),
        biz("Redirects served", total("wispurl_redirects_total", 'result="found"')),
        biz("Clicks recorded", total("wispurl_clicks_recorded_total")),
        biz("QR codes generated", total("wispurl_qr_codes_generated_total")),
        biz("Notifications sent", total("wispurl_notifications_total", 'result="sent"')),
    ], height=4)

    L.row("Infrastructure")
    infra = lambda p, uid, name: (dict(p, fieldConfig={**p["fieldConfig"], "defaults": {**p["fieldConfig"]["defaults"], "links": [link_to(uid, f"Open {name}")]}}), 4)  # noqa: E731
    L.add([
        infra(gauge("Host CPU", f'1 - avg(rate(node_cpu_seconds_total{{mode="idle"}}[{RI}]))'), "wispurl-host", "Docker Host"),
        infra(gauge("Host memory", "1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes"), "wispurl-host", "Docker Host"),
        infra(gauge("Docker data disk", '1 - min(node_filesystem_avail_bytes{mountpoint=~"/|/var/lib/docker", fstype!~"tmpfs|erofs"} / node_filesystem_size_bytes{mountpoint=~"/|/var/lib/docker", fstype!~"tmpfs|erofs"})'), "wispurl-host", "Docker Host"),
        infra(gauge("PostgreSQL connections", "sum(pg_stat_activity_count) / max(pg_settings_max_connections)"), "wispurl-postgres", "PostgreSQL"),
        infra(stat("Redis", "redis_up", thresholds=[(None, "red"), (1, "green")]), "wispurl-redis", "Redis"),
        infra(stat("Messages waiting", "sum(rabbitmq_detailed_queue_messages_ready) or vector(0)", thresholds=[(None, "green"), (100, "orange"), (1000, "red")]), "wispurl-rabbitmq", "RabbitMQ"),
    ], height=6)
    return dashboard("wispurl-overview", "WispURL — System Overview", "overview",
                     "Start here: is anything broken, who is affected, and where to look next.", L)


def business() -> tuple:
    L = Layout()
    L.row("Totals for the selected time range")
    L.add([
        (stat("New accounts", total("wispurl_auth_events_total", 'action="signup",result="success"')), 3),
        (stat("Successful logins", total("wispurl_auth_events_total", 'action="login",result="success"')), 3),
        (stat("Failed logins", total("wispurl_auth_events_total", 'action="login",result!="success"'),
              desc="Wrong passwords, inactive accounts and throttled attempts. A spike can mean credential stuffing."), 3),
        (stat("Links created", total("wispurl_links_created_total")), 3),
        (stat("Redirects served", total("wispurl_redirects_total", 'result="found"')), 3),
        (stat("Clicks recorded", total("wispurl_clicks_recorded_total")), 3),
        (stat("Milestones reached", total("wispurl_link_milestones_total")), 3),
        (stat("QR codes", total("wispurl_qr_codes_generated_total")), 3),
    ], height=4)

    L.row("Accounts")
    L.add([
        (timeseries("Signups by outcome", [(f"sum by (result) (rate(wispurl_auth_events_total{{action=\"signup\"}}[{RI}]))", "{{result}}")], "ops", stack=True), 8),
        (timeseries("Logins by outcome", [(f"sum by (result) (rate(wispurl_auth_events_total{{action=\"login\"}}[{RI}]))", "{{result}}")], "ops", stack=True), 8),
        (timeseries("Login success ratio",
                    [(f'sum(rate(wispurl_auth_events_total{{action="login",result="success"}}[{RI}])) / sum(rate(wispurl_auth_events_total{{action="login"}}[{RI}]))', "success ratio")],
                    "percentunit", max_=1, desc="Falling ratio with rising volume suggests an attack or a broken login flow."), 8),
    ])

    L.row("Links")
    L.add([
        (timeseries("Links created", [(f"sum by (slug) (rate(wispurl_links_created_total[{RI}]))", "{{slug}} slug")], "ops", stack=True), 8),
        (timeseries("Link creations refused", [(f"sum by (reason) (rate(wispurl_link_create_rejections_total[{RI}]))", "{{reason}}")], "ops", stack=True,
                    desc="rate_limited = user hit CREATE_LINK_LIMIT; duplicate_slug = custom slug taken."), 8),
        (timeseries("Links deleted and expired", [
            (f"sum(rate(wispurl_links_deleted_total{{result=\"deleted\"}}[{RI}]))", "deleted by owner"),
            (f"sum(rate(wispurl_links_expired_total[{RI}]))", "expired (cleanup)"),
        ], "ops"), 8),
    ])

    L.row("Redirects (the product's core path)")
    L.add([
        (timeseries("Redirects by outcome", [(f"sum by (result) (rate(wispurl_redirects_total[{RI}]))", "{{result}}")], "ops", stack=True), 8),
        (timeseries("Redirect hit ratio",
                    [(f'sum(rate(wispurl_redirects_total{{result="found"}}[{RI}])) / sum(rate(wispurl_redirects_total[{RI}]))', "found / all lookups")],
                    "percentunit", max_=1, desc="Share of short-link lookups that resolved. A drop means broken or mistyped links are being shared."), 8),
        (timeseries("Redirect latency (shortener)", [
            (quantile(0.5, "http_request_duration_seconds", 'service="shortener-service",path="/{short_code}"'), "p50"),
            (quantile(0.95, "http_request_duration_seconds", 'service="shortener-service",path="/{short_code}"'), "p95"),
            (quantile(0.99, "http_request_duration_seconds", 'service="shortener-service",path="/{short_code}"'), "p99"),
        ], "s"), 8),
    ])

    L.row("Click pipeline (shortener → RabbitMQ → analytics consumer)")
    L.add([
        (timeseries("Clicks published vs recorded", [
            (f'sum(rate(wispurl_messages_published_total{{routing_key="link.clicked",result="ok"}}[{RI}]))', "published (shortener)"),
            (f"sum(rate(wispurl_clicks_recorded_total[{RI}]))", "recorded (analytics)"),
        ], "ops", desc="The two lines should overlap. A persistent gap means clicks are queuing or being lost."), 8),
        (stat("Clicks not recorded (range)",
              f'clamp_min(sum(increase(wispurl_messages_published_total{{routing_key="link.clicked",result="ok"}}[{RANGE}])) - (sum(increase(wispurl_clicks_recorded_total{{source="queue"}}[{RANGE}])) or vector(0)), 0) or vector(0)',
              thresholds=[(None, "green"), (1, "orange"), (50, "red")], desc="Published minus recorded over the range. Small values are normal while a click is in flight."), 4),
        (stat("Click publish failures (range)", total("wispurl_messages_published_total", 'routing_key="link.clicked",result="error"'), thresholds=ZERO_GOOD,
              desc="Redirects whose click event never reached RabbitMQ (the redirect itself still worked)."), 4),
        (timeseries("Milestones reached", [(f"sum by (threshold) (increase(wispurl_link_milestones_total[{RI}]))", "{{threshold}} clicks")], "short", bars=True), 8),
    ])

    L.row("Other features")
    L.add([
        (timeseries("QR codes by size", [(f"sum by (size) (rate(wispurl_qr_codes_generated_total[{RI}]))", "{{size}}")], "ops", stack=True), 6),
        (timeseries("Rate-limit decisions", [(f"sum by (decision) (rate(wispurl_rate_limit_decisions_total[{RI}]))", "{{decision}}")], "ops", stack=True), 6),
        (timeseries("Rate limiter unavailable", [(f"sum by (fallback) (rate(wispurl_rate_limiter_unavailable_total[{RI}]))", "fallback: {{fallback}}")], "ops",
                    desc="The shortener couldn't reach the rate limiter and applied RATE_LIMITER_FAIL_OPEN."), 6),
        (timeseries("Notifications", [(f"sum by (type, result) (rate(wispurl_notifications_total[{RI}]))", "{{type}} {{result}}")], "ops", stack=True), 6),
    ])
    return dashboard("wispurl-business", "WispURL — Business", "overview",
                     "What the product is doing: accounts, links, redirects, clicks and notifications.", L, time="now-24h")


def service_detail() -> tuple:
    S = 'service="$service"'
    SR = 'service="$service",path=~"$route"'
    L = Layout()
    L.row("Golden signals for $service")
    L.add([
        (stat("Instances up", 'sum(up{compose_service="$service"})', thresholds=[(None, "red"), (1, "green")]), 3),
        (stat("Requests/s", f"sum(rate(http_requests_total{{{SR}}}[{RI}]))", "reqps", graph=True), 3),
        (stat("5xx ratio", err_ratio(SR), "percentunit", thresholds=ERR_THRESH, decimals=2), 3),
        (stat("4xx ratio",
              f'(sum(rate(http_requests_total{{{SR},status=~"4.."}}[{RI}])) or vector(0)) / sum(rate(http_requests_total{{{SR}}}[{RI}]))',
              "percentunit", decimals=2, desc="Client errors: bad input, auth failures, not found. Usually not your bug, but a sudden jump can be."), 3),
        (stat("p50 latency", quantile(0.5, "http_request_duration_seconds", SR), "s"), 3),
        (stat("p95 latency", quantile(0.95, "http_request_duration_seconds", SR), "s", thresholds=LAT_THRESH), 3),
        (stat("p99 latency", quantile(0.99, "http_request_duration_seconds", SR), "s", thresholds=LAT_THRESH), 3),
        (stat("In progress", f"sum(http_requests_in_progress{{{S}}})", desc="Requests being handled right now: the saturation signal."), 3),
    ], height=4)

    L.row("Traffic")
    L.add([
        (timeseries("Requests per second by route", [(f"sum by (path) (rate(http_requests_total{{{SR}}}[{RI}]))", "{{path}}")], "reqps", stack=True), 12),
        (timeseries("Responses by status", [(f"sum by (status) (rate(http_requests_total{{{SR}}}[{RI}]))", "{{status}}")], "reqps", stack=True), 12),
    ])

    L.row("Errors")
    L.add([
        (timeseries("5xx per second by route", [(f"sum by (path, status) (rate(http_requests_total{{{SR},{FAILED}}}[{RI}]))", "{{status}} {{path}}")], "reqps"), 8),
        (timeseries("4xx per second by route", [(f'sum by (path, status) (rate(http_requests_total{{{SR},status=~"4.."}}[{RI}]))', "{{status}} {{path}}")], "reqps"), 8),
        (timeseries("5xx ratio", [(err_ratio(SR), "5xx ratio")], "percentunit", thresholds=ERR_THRESH), 8),
    ])

    L.row("Latency")
    L.add([
        (timeseries("Latency percentiles", [
            (quantile(0.5, "http_request_duration_seconds", SR), "p50"),
            (quantile(0.95, "http_request_duration_seconds", SR), "p95"),
            (quantile(0.99, "http_request_duration_seconds", SR), "p99"),
        ], "s", thresholds=LAT_THRESH), 8),
        (timeseries("p95 latency by route", [(quantile(0.95, "http_request_duration_seconds", SR, "path"), "{{path}}")], "s"), 8),
        (heatmap("Latency distribution", f"sum by (le) (rate(http_request_duration_seconds_bucket{{{SR}}}[{RI}]))",
                 desc="Each column is a time slice; darker cells hold more requests. Two bands mean two populations (e.g. cache hits and misses)."), 8),
    ])

    L.row("Dependencies (from traces)")
    client = 'service="$service",span_kind="SPAN_KIND_CLIENT"'
    L.add([
        (timeseries("Outgoing calls per second", [(f"sum by (span_name) (rate(traces_spanmetrics_calls_total{{{client}}}[{RI}]))", "{{span_name}}")], "ops",
                    desc="Every SQL statement, Redis command and HTTP call this service makes, from Tempo span metrics."), 8),
        (timeseries("p95 duration of outgoing calls", [(quantile(0.95, "traces_spanmetrics_latency", client, "span_name"), "{{span_name}}")], "s"), 8),
        (timeseries("Calls to other services and stores", [
            (f'sum by (server) (rate(traces_service_graph_request_total{{client="$service"}}[{RI}]))', "→ {{server}}"),
            (f'sum by (server) (rate(traces_service_graph_request_failed_total{{client="$service"}}[{RI}]))', "→ {{server}} failed"),
        ], "ops", desc="From Tempo's service graph: which services and databases this one calls."), 8),
    ])

    L.row("Business events from $service")
    L.add([(timeseries(
        "Business counters",
        [(f'sum by (__name__, action, result, reason, slug, decision, size, source, routing_key) (rate({{__name__=~"wispurl_.+_total", compose_service="$service"}}[{RI}]))',
          "{{__name__}} {{action}} {{result}}{{reason}}{{slug}}{{decision}}{{size}}{{source}}{{routing_key}}")],
        "ops", desc="Every wispurl_* counter this service exports. See the Business dashboard for the product-wide view."), 24)])

    L.row("Resources")
    C = 'container_label_com_docker_compose_service="$service"'
    L.add([
        (timeseries("CPU (cores)", [(f"sum by (name) (rate(container_cpu_usage_seconds_total{{{C}}}[{RI}]))", "{{name}}")], "short"), 8),
        (timeseries("Memory (working set)", [(f"sum by (name) (container_memory_working_set_bytes{{{C}}})", "{{name}}")], "bytes"), 8),
        # cAdvisor can't see per-container network traffic on Docker Desktop, so
        # the third resource panel is disk I/O, which it does report.
        (timeseries("Disk I/O", [
            (f"sum by (name) (rate(container_fs_reads_bytes_total{{{C}}}[{RI}]))", "{{name}} read"),
            (f"-sum by (name) (rate(container_fs_writes_bytes_total{{{C}}}[{RI}]))", "{{name}} written"),
        ], "Bps", min_=None), 8),
    ])

    L.row("Logs and traces")
    L.add([
        (log_volume("Log lines by level", 'sum by (level) (count_over_time({service="$service", level=~"$level"}[$__interval]))', "{{level}}"), 8),
        (traces("Slowest recent requests", '{ resource.service.name = "$service" && kind = server && duration > 200ms }',
                desc="Click a trace ID to open it in Tempo."), 8),
        (traces("Failed requests", '{ resource.service.name = "$service" && status = error }'), 8),
    ])
    L.add([(logs("Logs", '{service="$service", level=~"$level"}'), 24)], height=12)

    variables = [
        query_var("service", "Service", 'label_values(http_requests_total, service)'),
        query_var("route", "Route", 'label_values(http_requests_total{service="$service"}, path)', multi=True, include_all=True),
        custom_var("level", "Log level", ["error", "critical", "warning", "info", "debug"]),
    ]
    return dashboard("wispurl-service", "Service Detail", "applications",
                     "Everything about one HTTP service: RED metrics per route, dependencies, business events, resources, logs and traces.", L, variables)


def workers() -> tuple:
    Q = 'queue=~"$queue"'
    W = 'compose_service="$worker"'
    L = Layout()
    L.row("Queues")
    L.add([
        (stat("Ready (selected queues)", f"sum(rabbitmq_detailed_queue_messages_ready{{{Q}}}) or vector(0)", thresholds=[(None, "green"), (100, "orange"), (1000, "red")]), 4),
        (stat("Unacknowledged", f"sum(rabbitmq_detailed_queue_messages_unacked{{{Q}}}) or vector(0)"), 4),
        (stat("Dead-letter queue", 'sum(rabbitmq_detailed_queue_messages{queue="events.dlq"}) or vector(0)', thresholds=ZERO_GOOD), 4),
        (stat("Processed/s", f"sum(rate(wispurl_messages_processed_total{{{Q}}}[{RI}])) or vector(0)", "ops", graph=True), 4),
        (stat("Retries (range)", total("wispurl_messages_processed_total", f'{Q},result="retry"'), thresholds=[(None, "green"), (1, "orange")]), 4),
        (stat("Dead-lettered (range)", total("wispurl_messages_processed_total", f'{Q},result=~"dead_letter|malformed"'), thresholds=ZERO_GOOD), 4),
    ], height=4)
    L.add([
        (timeseries("Messages waiting by queue", [(f"sum by (queue) (rabbitmq_detailed_queue_messages_ready{{{Q}}})", "{{queue}}")], "short",
                    desc="A queue that keeps growing means its consumer can't keep up."), 8),
        (timeseries("Unacknowledged by queue", [(f"sum by (queue) (rabbitmq_detailed_queue_messages_unacked{{{Q}}})", "{{queue}}")], "short",
                    desc="Delivered to a consumer but not yet acknowledged: messages being worked on."), 8),
        (timeseries("Consumers by queue", [(f"sum by (queue) (rabbitmq_detailed_queue_consumers{{{Q}}})", "{{queue}}")], "short",
                    desc="0 on a work queue means nothing is reading it."), 8),
    ])

    L.row("Processing")
    L.add([
        (timeseries("Outcome per second", [(f"sum by (queue, result) (rate(wispurl_messages_processed_total{{{Q}}}[{RI}]))", "{{queue}} {{result}}")], "ops", stack=True), 8),
        (timeseries("Processing time p95", [(quantile(0.95, "wispurl_message_processing_seconds", Q, "queue"), "{{queue}}")], "s"), 8),
        (timeseries("Success ratio", [(f'sum by (queue) (rate(wispurl_messages_processed_total{{{Q},result="ack"}}[{RI}])) / sum by (queue) (rate(wispurl_messages_processed_total{{{Q}}}[{RI}]))', "{{queue}}")],
                    "percentunit", max_=1), 8),
    ])

    L.row("Publishing")
    L.add([
        (timeseries("Published per second", [(f"sum by (routing_key) (rate(wispurl_messages_published_total{{result=\"ok\"}}[{RI}]))", "{{routing_key}}")], "ops", stack=True), 12),
        (timeseries("Publish failures", [(f"sum by (routing_key, compose_service) (rate(wispurl_messages_published_total{{result=\"error\"}}[{RI}]))", "{{compose_service}} {{routing_key}}")], "ops"), 12),
    ])

    L.row("Worker: $worker")
    C = 'container_label_com_docker_compose_service="$worker"'
    L.add([
        (stat("Up", f"sum(up{{{W}}})", thresholds=[(None, "red"), (1, "green")]), 3),
        (timeseries("CPU (cores)", [(f"sum by (name) (rate(container_cpu_usage_seconds_total{{{C}}}[{RI}]))", "{{name}}")], "short"), 7),
        (timeseries("Memory (working set)", [(f"sum by (name) (container_memory_working_set_bytes{{{C}}})", "{{name}}")], "bytes"), 7),
        (timeseries("Business counters", [(f'sum by (__name__, result, source, type, outcome) (rate({{__name__=~"wispurl_.+_total", {W}}}[{RI}]))', "{{__name__}} {{type}} {{result}}{{source}}{{outcome}}")], "ops"), 7),
    ])

    L.row("Cleanup sweeps")
    L.add([
        (timeseries("Sweeps per minute by outcome", [(f"sum by (outcome) (rate(wispurl_cleanup_sweep_seconds_count[{RI}])) * 60", "{{outcome}}")], "short", stack=True), 8),
        (timeseries("Sweep duration p95", [(quantile(0.95, "wispurl_cleanup_sweep_seconds", ""), "p95")], "s"), 8),
        (timeseries("Links expired", [(f"sum(increase(wispurl_links_expired_total[{RI}]))", "expired")], "short", bars=True), 8),
    ])

    L.row("Notifications")
    L.add([
        (timeseries("Notifications by type and outcome", [(f"sum by (type, result, channel) (rate(wispurl_notifications_total[{RI}]))", "{{type}} {{result}} ({{channel}})")], "ops", stack=True), 24),
    ])

    L.add([(logs("Worker logs", '{service="$worker", level=~"$level"}'), 24)], height=12)
    variables = [
        query_var("worker", "Worker", f'label_values(up{{job="docker-compose-services", compose_service=~"{WORKERS}"}}, compose_service)'),
        query_var("queue", "Queue", "label_values(rabbitmq_detailed_queue_messages, queue)", multi=True, include_all=True),
        custom_var("level", "Log level", ["error", "critical", "warning", "info", "debug"]),
    ]
    return dashboard("wispurl-workers", "Workers & Messaging", "applications",
                     "Queue depth, processing outcomes, retries and dead-lettering, publishing, and each worker's resources and logs.", L, variables)


def host() -> tuple:
    L = Layout()
    cores = 'count(node_cpu_seconds_total{mode="idle"})'
    disk_sel = 'mountpoint=~"/|/var/lib/docker", fstype!~"tmpfs|erofs"'
    net = 'device=~"eth.*"'
    L.row("Utilization")
    L.add([
        (gauge("CPU", f'1 - avg(rate(node_cpu_seconds_total{{mode="idle"}}[{RI}]))'), 4),
        (gauge("Memory", "1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes"), 4),
        (gauge("Docker data disk", f"1 - min(node_filesystem_avail_bytes{{{disk_sel}}} / node_filesystem_size_bytes{{{disk_sel}}})"), 4),
        (stat("CPUs", cores), 3),
        (stat("Memory total", "node_memory_MemTotal_bytes", "bytes"), 3),
        (stat("Load (1m) per CPU", f"node_load1 / scalar({cores})", "percentunit", thresholds=[(None, "green"), (0.8, "orange"), (1, "red")],
              desc="Above 100% means work is queuing for a CPU (saturation)."), 3),
        (stat("Uptime", "node_time_seconds - node_boot_time_seconds", "s"), 3),
    ], height=5)
    L.row("CPU")
    L.add([
        (timeseries("CPU by mode", [(f'sum by (mode) (rate(node_cpu_seconds_total{{mode!="idle"}}[{RI}])) / scalar({cores})', "{{mode}}")], "percentunit", stack=True, max_=1), 12),
        (timeseries("Load average vs CPUs", [("node_load1", "1m"), ("node_load5", "5m"), ("node_load15", "15m"), (cores, "CPUs")], "short"), 12),
    ])
    L.row("Memory and disk")
    L.add([
        (timeseries("Memory", [
            ("node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes", "used"),
            ("node_memory_Cached_bytes + node_memory_Buffers_bytes", "cache and buffers"),
            ("node_memory_MemAvailable_bytes", "available"),
        ], "bytes"), 8),
        (timeseries("Disk throughput", [
            (f"sum(rate(node_disk_read_bytes_total[{RI}]))", "read"),
            (f"-sum(rate(node_disk_written_bytes_total[{RI}]))", "written"),
        ], "Bps", min_=None), 8),
        (timeseries("Disk busy", [(f"max(rate(node_disk_io_time_seconds_total[{RI}]))", "busiest disk")], "percentunit", max_=1,
                    desc="Share of time the busiest disk was handling I/O. Near 100% means disk saturation."), 8),
    ])
    L.row("Network")
    L.add([
        (timeseries("Network throughput", [
            (f"sum by (device) (rate(node_network_receive_bytes_total{{{net}}}[{RI}]))", "{{device}} in"),
            (f"-sum by (device) (rate(node_network_transmit_bytes_total{{{net}}}[{RI}]))", "{{device}} out"),
        ], "Bps", min_=None), 12),
        (timeseries("Network errors", [(f"sum by (device) (rate(node_network_receive_errs_total{{{net}}}[{RI}]))", "{{device}} receive errors")], "short"), 12),
    ])
    return dashboard("wispurl-host", "Docker Host", "infrastructure",
                     "USE metrics for the machine running Docker (on Docker Desktop: Docker's Linux VM).", L)


def containers() -> tuple:
    C = 'container_label_com_docker_compose_project=~"$project", name=~"$container"'
    L = Layout()
    L.row("All containers")
    L.add([(table(
        "Containers",
        [
            (f"sum by (name) (rate(container_cpu_usage_seconds_total{{{C}}}[{RI}]))", ""),
            (f"sum by (name) (container_memory_working_set_bytes{{{C}}})", ""),
            (f"sum by (name) (rate(container_fs_reads_bytes_total{{{C}}}[{RI}]))", ""),
            (f"sum by (name) (rate(container_fs_writes_bytes_total{{{C}}}[{RI}]))", ""),
            (f"max by (name) (time() - container_start_time_seconds{{{C}}})", ""),
        ],
        join_on="name",
        columns={"Value #A": ("CPU (cores)", "short"), "Value #B": ("Memory", "bytes"), "Value #C": ("Disk read", "Bps"), "Value #D": ("Disk write", "Bps"), "Value #E": ("Running for", "s")},
    ), 24)], height=10)
    L.row("Usage over time")
    L.add([
        (timeseries("CPU (cores)", [(f"sum by (name) (rate(container_cpu_usage_seconds_total{{{C}}}[{RI}]))", "{{name}}")], "short"), 12),
        (timeseries("Memory (working set)", [(f"sum by (name) (container_memory_working_set_bytes{{{C}}})", "{{name}}")], "bytes"), 12),
    ])
    L.add([
        (timeseries("Disk reads", [(f"sum by (name) (rate(container_fs_reads_bytes_total{{{C}}}[{RI}]))", "{{name}}")], "Bps"), 8),
        (timeseries("Disk writes", [(f"sum by (name) (rate(container_fs_writes_bytes_total{{{C}}}[{RI}]))", "{{name}}")], "Bps"), 8),
        (timeseries("Out-of-memory kills", [(f"sum by (name) (increase(container_oom_events_total{{{C}}}[{RI}]))", "{{name}}")], "short", bars=True,
                    desc="Any bar here means the kernel killed a process in that container for using too much memory."), 8),
    ])
    variables = [
        query_var("project", "Compose project", 'label_values(container_memory_working_set_bytes{name!=""}, container_label_com_docker_compose_project)', multi=True, include_all=True),
        query_var("container", "Container", 'label_values(container_memory_working_set_bytes{container_label_com_docker_compose_project=~"$project", name!=""}, name)', multi=True, include_all=True),
    ]
    return dashboard("wispurl-containers", "Containers", "infrastructure",
                     "CPU, memory and disk per container (cAdvisor). Per-container network traffic isn't available under Docker Desktop.", L, variables)


def postgres() -> tuple:
    D = 'datname=~"$database"'
    L = Layout()
    L.row("Health")
    L.add([
        (stat("Up", "pg_up", thresholds=[(None, "red"), (1, "green")]), 4),
        (gauge("Connections used", "sum(pg_stat_activity_count) / max(pg_settings_max_connections)"), 4),
        (stat("Longest transaction", f"max(pg_stat_activity_max_tx_duration{{{D}}})", "s", thresholds=[(None, "green"), (30, "orange"), (60, "red")],
              desc="Long transactions hold locks and block cleanup. WispURL kills idle-in-transaction sessions after 60 s."), 4),
        (stat("Database size", f"sum(pg_database_size_bytes{{{D}}})", "bytes"), 4),
        (stat("Cache hit ratio", f"sum(rate(pg_stat_database_blks_hit{{{D}}}[{RI}])) / (sum(rate(pg_stat_database_blks_hit{{{D}}}[{RI}])) + sum(rate(pg_stat_database_blks_read{{{D}}}[{RI}])))",
              "percentunit", thresholds=[(None, "red"), (0.9, "orange"), (0.99, "green")], decimals=2,
              desc="Share of reads served from memory. Below ~99% on a small database means memory pressure."), 4),
        (stat("Deadlocks (range)", total("pg_stat_database_deadlocks", D), thresholds=ZERO_GOOD), 4),
    ], height=5)
    L.row("Connections")
    L.add([
        (timeseries("Connections by state", [(f"sum by (state) (pg_stat_activity_count{{{D}}})", "{{state}}")], "short", stack=True), 8),
        (timeseries("Connections by database", [(f"sum by (datname) (pg_stat_activity_count{{{D}}})", "{{datname}}")], "short", stack=True), 8),
        (timeseries("Connections vs max", [("sum(pg_stat_activity_count)", "in use"), ("max(pg_settings_max_connections)", "max_connections")], "short"), 8),
    ])
    L.row("Throughput")
    L.add([
        (timeseries("Transactions per second", [
            (f"sum by (datname) (rate(pg_stat_database_xact_commit{{{D}}}[{RI}]))", "{{datname}} commit"),
            (f"sum by (datname) (rate(pg_stat_database_xact_rollback{{{D}}}[{RI}]))", "{{datname}} rollback"),
        ], "ops"), 8),
        (timeseries("Rows per second", [
            (f"sum(rate(pg_stat_database_tup_fetched{{{D}}}[{RI}]))", "fetched"),
            (f"sum(rate(pg_stat_database_tup_inserted{{{D}}}[{RI}]))", "inserted"),
            (f"sum(rate(pg_stat_database_tup_updated{{{D}}}[{RI}]))", "updated"),
            (f"sum(rate(pg_stat_database_tup_deleted{{{D}}}[{RI}]))", "deleted"),
        ], "ops"), 8),
        (timeseries("Temporary files written", [(f"sum by (datname) (rate(pg_stat_database_temp_bytes{{{D}}}[{RI}]))", "{{datname}}")], "Bps",
                    desc="Queries spilling to disk because they didn't fit in work_mem."), 8),
    ])
    L.row("Storage and locks")
    L.add([
        (timeseries("Database size", [(f"sum by (datname) (pg_database_size_bytes{{{D}}})", "{{datname}}")], "bytes"), 12),
        (timeseries("Locks by mode", [(f"sum by (mode) (pg_locks_count{{{D}}})", "{{mode}}")], "short"), 12),
    ])
    variables = [query_var("database", "Database", "label_values(pg_stat_database_xact_commit, datname)", multi=True, include_all=True, regex="/^(?!template).*/")]
    return dashboard("wispurl-postgres", "PostgreSQL", "infrastructure", "Connections, transactions, cache efficiency, size and locks per database.", L, variables)


def redis() -> tuple:
    L = Layout()
    L.row("Health")
    L.add([
        (stat("Up", "redis_up", thresholds=[(None, "red"), (1, "green")]), 4),
        (stat("Uptime", "redis_uptime_in_seconds", "s"), 4),
        (stat("Clients", "redis_connected_clients"), 4),
        (stat("Memory used", "redis_memory_used_bytes", "bytes"), 4),
        (stat("Commands/s", f"rate(redis_commands_processed_total[{RI}])", "ops", graph=True), 4),
        (stat("Rejected connections (range)", total("redis_rejected_connections_total"), thresholds=ZERO_GOOD), 4),
    ], height=5)
    L.row("Activity")
    L.add([
        (timeseries("Commands per second", [(f"rate(redis_commands_processed_total[{RI}])", "commands")], "ops"), 8),
        (timeseries("Keyspace hit ratio", [(f"rate(redis_keyspace_hits_total[{RI}]) / (rate(redis_keyspace_hits_total[{RI}]) + rate(redis_keyspace_misses_total[{RI}]))", "hit ratio")],
                    "percentunit", max_=1, desc="For the rate limiter, misses are normal (first request in a window)."), 8),
        (timeseries("Clients", [("redis_connected_clients", "connected"), ("redis_blocked_clients", "blocked")], "short"), 8),
    ])
    L.add([
        (timeseries("Memory", [("redis_memory_used_bytes", "used")], "bytes"), 8),
        (timeseries("Keys by database", [("sum by (db) (redis_db_keys)", "{{db}}")], "short"), 8),
        (timeseries("Expired and evicted keys", [
            (f"rate(redis_expired_keys_total[{RI}])", "expired (TTL)"),
            (f"rate(redis_evicted_keys_total[{RI}])", "evicted (memory pressure)"),
        ], "ops", desc="Evictions mean Redis ran out of memory and dropped keys early."), 8),
    ])
    return dashboard("wispurl-redis", "Redis", "infrastructure", "The rate limiter's store: clients, throughput, memory and keys.", L)


def rabbitmq() -> tuple:
    Q = 'queue=~"$queue"'
    L = Layout()
    L.row("Broker")
    L.add([
        (stat("Queues", "rabbitmq_queues"), 3),
        (stat("Connections", "rabbitmq_connections"), 3),
        (stat("Channels", "rabbitmq_channels"), 3),
        (stat("Consumers", "rabbitmq_consumers"), 3),
        (gauge("Memory vs limit", "rabbitmq_process_resident_memory_bytes / rabbitmq_resident_memory_limit_bytes",
               desc="At 100% RabbitMQ blocks publishers until memory frees up."), 4),
        (stat("Disk free", "rabbitmq_disk_space_available_bytes", "bytes"), 4),
        (stat("Alarms", "rabbitmq_alarms_memory_used_watermark + rabbitmq_alarms_free_disk_space_watermark", thresholds=ZERO_GOOD,
              desc="A memory or disk alarm blocks all publishing."), 4),
    ], height=5)
    L.row("Message flow")
    L.add([
        (timeseries("Messages per second", [
            (f"sum(rate(rabbitmq_global_messages_received_total[{RI}]))", "received"),
            (f"sum(rate(rabbitmq_global_messages_routed_total[{RI}]))", "routed"),
            (f"sum(rate(rabbitmq_global_messages_delivered_total[{RI}]))", "delivered"),
            (f"sum(rate(rabbitmq_global_messages_acknowledged_total[{RI}]))", "acknowledged"),
        ], "ops"), 12),
        (timeseries("Problem messages", [
            (f"sum(rate(rabbitmq_global_messages_redelivered_total[{RI}]))", "redelivered"),
            (f"sum(rate(rabbitmq_global_messages_unroutable_dropped_total[{RI}]))", "unroutable (dropped)"),
        ], "ops", desc="Unroutable messages matched no queue binding and were lost."), 12),
    ])
    L.row("Queues: $queue")
    L.add([
        (timeseries("Ready", [(f"sum by (queue) (rabbitmq_detailed_queue_messages_ready{{{Q}}})", "{{queue}}")], "short"), 8),
        (timeseries("Unacknowledged", [(f"sum by (queue) (rabbitmq_detailed_queue_messages_unacked{{{Q}}})", "{{queue}}")], "short"), 8),
        (timeseries("Consumers", [(f"sum by (queue) (rabbitmq_detailed_queue_consumers{{{Q}}})", "{{queue}}")], "short"), 8),
    ])
    L.row("Resources")
    L.add([
        (timeseries("Memory", [("rabbitmq_process_resident_memory_bytes", "used"), ("rabbitmq_resident_memory_limit_bytes", "limit")], "bytes"), 12),
        (timeseries("Disk free", [("rabbitmq_disk_space_available_bytes", "free"), ("rabbitmq_disk_space_available_limit_bytes", "alarm threshold")], "bytes"), 12),
    ])
    variables = [query_var("queue", "Queue", "label_values(rabbitmq_detailed_queue_messages, queue)", multi=True, include_all=True)]
    return dashboard("wispurl-rabbitmq", "RabbitMQ", "infrastructure", "Broker health, message flow and per-queue depth.", L, variables)


def prometheus() -> tuple:
    L = Layout()
    L.row("Health")
    L.add([
        (stat("Up", 'up{job="prometheus"}', thresholds=[(None, "red"), (1, "green")]), 3),
        (stat("Config reload OK", "prometheus_config_last_reload_successful", thresholds=[(None, "red"), (1, "green")]), 3),
        (stat("Active series", "prometheus_tsdb_head_series", graph=True), 4),
        (stat("Samples/s", f"rate(prometheus_tsdb_head_samples_appended_total[{RI}])", "ops", graph=True), 4),
        (stat("Storage", "prometheus_tsdb_storage_blocks_bytes + prometheus_tsdb_wal_storage_size_bytes", "bytes",
              desc="Blocks plus write-ahead log. Retention keeps this under 5 GB."), 4),
        (stat("Rule evaluation failures (range)", total("prometheus_rule_evaluation_failures_total"), thresholds=ZERO_GOOD), 4),
    ], height=5)
    L.row("Ingestion and storage")
    L.add([
        (timeseries("Active series", [("prometheus_tsdb_head_series", "series")], "short",
                    desc="Memory grows with series. A sudden jump usually means a new high-cardinality label."), 8),
        (timeseries("Samples appended per second", [(f"rate(prometheus_tsdb_head_samples_appended_total[{RI}])", "samples")], "ops"), 8),
        (timeseries("Storage", [("prometheus_tsdb_storage_blocks_bytes", "blocks"), ("prometheus_tsdb_wal_storage_size_bytes", "WAL")], "bytes", stack=True), 8),
    ])
    L.row("Requests and alerting")
    L.add([
        (timeseries("HTTP requests by handler", [(f'sum by (handler) (rate(prometheus_http_requests_total{{handler=~"/api/v1/(write|query|query_range|series|labels)"}}[{RI}]))', "{{handler}}")], "reqps",
                    desc="/api/v1/write is remote write from Alloy and Tempo."), 8),
        (timeseries("Alerts sent to Alertmanager", [
            (f"sum(rate(prometheus_notifications_sent_total[{RI}]))", "sent"),
            (f"sum(rate(prometheus_notifications_dropped_total[{RI}]))", "dropped"),
        ], "ops"), 8),
        (timeseries("Rule group evaluation time", [("max by (rule_group) (prometheus_rule_group_last_duration_seconds)", "{{rule_group}}")], "s"), 8),
    ])
    L.row("Targets scraped directly by Prometheus")
    L.add([(table("Targets", [('up{application="observability"}', "")], join_on="job", columns={"Value": ("Up", "short")}, extra_fields=("instance",),
                  thresholds={"Value": [(None, "red"), (1, "green")]}, desc="App targets are scraped by Alloy; see the Alloy dashboard."), 24)], height=7)
    return dashboard("wispurl-prometheus", "Prometheus", "observability", "Is the metrics store healthy, how big is it, and are rules and alerts working?", L)


def loki() -> tuple:
    L = Layout()
    L.row("Health")
    L.add([
        (stat("Up", 'up{job="loki"}', thresholds=[(None, "red"), (1, "green")]), 4),
        (stat("Lines/s", f"sum(rate(loki_distributor_lines_received_total[{RI}]))", "ops", graph=True), 5),
        (stat("Ingest bytes/s", f"sum(rate(loki_distributor_bytes_received_total[{RI}]))", "Bps", graph=True), 5),
        (stat("Streams in memory", "sum(loki_ingester_memory_streams)"), 5),
        (stat("Discarded lines (range)", total("loki_discarded_samples_total"), thresholds=ZERO_GOOD,
              desc="Rejected by limits (rate, age, size). See the panel below for reasons."), 5),
    ], height=5)
    L.row("Log volume (from Loki itself)")
    L.add([
        (log_volume("Lines by service", 'sum by (service) (count_over_time({application="wispurl"}[$__interval]))', "{{service}}"), 12),
        (log_volume("Lines by level", 'sum by (level) (count_over_time({application="wispurl", level=~".+"}[$__interval]))', "{{level}}"), 12),
    ])
    L.row("Internals")
    L.add([
        (timeseries("Discarded lines by reason", [(f"sum by (reason) (rate(loki_discarded_samples_total[{RI}]))", "{{reason}}")], "ops"), 8),
        (timeseries("Request p95 by route", [(quantile(0.95, "loki_request_duration_seconds", 'route=~"loki_api_v1_.*"', "route"), "{{route}}")], "s"), 8),
        (stat("Last retention run", "time() - max(loki_compactor_apply_retention_last_successful_run_timestamp_seconds)", "s",
              thresholds=[(None, "green"), (3600, "orange"), (86400, "red")], desc="How long since the compactor last applied retention. It runs every 10 minutes."), 8),
    ])
    return dashboard("wispurl-loki", "Loki", "observability", "Log ingestion, volume by service and level, rejections and retention.", L)


def tempo() -> tuple:
    L = Layout()
    L.row("Health")
    L.add([
        (stat("Up", 'up{job="tempo"}', thresholds=[(None, "red"), (1, "green")]), 4),
        (stat("Spans/s", f"sum(rate(tempo_distributor_spans_received_total[{RI}]))", "ops", graph=True), 5),
        (stat("Ingest bytes/s", f"sum(rate(tempo_distributor_bytes_received_total[{RI}]))", "Bps", graph=True), 5),
        (stat("Live traces", "sum(tempo_live_store_live_traces)"), 5),
        (stat("Discarded spans (range)", total("tempo_discarded_spans_total"), thresholds=ZERO_GOOD), 5),
    ], height=5)
    L.row("Ingestion")
    L.add([
        (timeseries("Spans received per second", [(f"sum(rate(tempo_distributor_spans_received_total[{RI}]))", "spans")], "ops"), 8),
        (timeseries("Spans into the metrics generator", [(f"sum(rate(tempo_metrics_generator_spans_received_total[{RI}]))", "spans")], "ops",
                    desc="Source of span metrics and the service graph."), 8),
        (timeseries("Block completion failures", [(f"sum(rate(tempo_live_store_failed_completions_total[{RI}]))", "failed")], "ops"), 8),
    ])
    L.row("Queries")
    L.add([(timeseries("Request p95 by route", [(quantile(0.95, "tempo_request_duration_seconds", 'route=~"(querier_)?api_.*"', "route"), "{{route}}")], "s",
                                desc="Fills in as traces are searched in Grafana."), 24)])
    return dashboard("wispurl-tempo", "Tempo", "observability", "Trace ingestion, the metrics generator and query latency.", L)


def alloy() -> tuple:
    L = Layout()
    L.row("Health")
    L.add([
        (stat("Up", 'up{job="alloy"}', thresholds=[(None, "red"), (1, "green")]), 3),
        (stat("Running components", "sum(alloy_component_controller_running_components)"), 3),
        (stat("App targets scraped", f"count({UP_APPS})"), 3),
        (stat("Samples pending", "sum(prometheus_remote_storage_samples_pending) or vector(0)", thresholds=[(None, "green"), (10000, "orange")],
              desc="Waiting in the remote-write buffer. Growing means Prometheus is slow or down."), 3),
        (stat("Samples failed (range)", total("prometheus_remote_storage_samples_failed_total"), thresholds=ZERO_GOOD), 4),
        (stat("Log entries dropped (range)", total("loki_write_dropped_entries_total"), thresholds=ZERO_GOOD), 4),
        (stat("Span export failures (range)", total("otelcol_exporter_send_failed_spans_total"), thresholds=ZERO_GOOD), 4),
    ], height=5)
    L.row("Metrics pipeline (scrape → remote write)")
    L.add([
        (timeseries("Samples sent per second", [(f"sum(rate(prometheus_remote_storage_samples_total[{RI}]))", "sent")], "ops"), 8),
        (timeseries("Retried and failed", [
            (f"sum(rate(prometheus_remote_storage_samples_retried_total[{RI}]))", "retried"),
            (f"sum(rate(prometheus_remote_storage_samples_failed_total[{RI}])) or vector(0)", "failed"),
        ], "ops"), 8),
        (timeseries("Pending samples", [("sum(prometheus_remote_storage_samples_pending)", "pending")], "short"), 8),
    ])
    L.row("Logs pipeline (Docker → process → Loki)")
    L.add([
        (timeseries("Entries sent to Loki", [(f"sum(rate(loki_write_sent_entries_total[{RI}]))", "sent"), (f"sum(rate(loki_write_dropped_entries_total[{RI}])) or vector(0)", "dropped")], "ops"), 8),
        (timeseries("Lines dropped by the pipeline", [(f"sum by (reason) (rate(loki_process_dropped_lines_total[{RI}]))", "{{reason}}")], "ops",
                    desc="Intentional drops, e.g. probe_noise from the stage.drop rule."), 8),
        (timeseries("Bytes sent to Loki", [(f"sum(rate(loki_write_sent_bytes_total[{RI}]))", "bytes")], "Bps"), 8),
    ])
    L.row("Traces pipeline (OTLP → batch → Tempo)")
    L.add([
        (timeseries("Spans accepted and refused", [
            (f"sum(rate(otelcol_receiver_accepted_spans_total[{RI}]))", "accepted"),
            (f"sum(rate(otelcol_receiver_refused_spans_total[{RI}])) or vector(0)", "refused"),
        ], "ops"), 12),
        (timeseries("Spans exported to Tempo", [
            (f"sum(rate(otelcol_exporter_sent_spans_total[{RI}]))", "sent"),
            (f"sum(rate(otelcol_exporter_send_failed_spans_total[{RI}])) or vector(0)", "failed"),
        ], "ops"), 12),
    ])
    return dashboard("wispurl-alloy", "Alloy", "observability", "The collector: metrics, logs and traces pipelines, buffers and failures.", L)


def alerting() -> tuple:
    L = Layout()
    L.row("Now")
    L.add([
        (stat("Firing", 'count(ALERTS{alertstate="firing"}) or vector(0)', thresholds=ZERO_GOOD), 4),
        (stat("Pending", 'count(ALERTS{alertstate="pending"}) or vector(0)', thresholds=[(None, "green"), (1, "orange")]), 4),
        (stat("Active silences", 'sum(alertmanager_silences{state="active"}) or vector(0)'), 4),
        (stat("Notifications failed (range)", total("alertmanager_notifications_failed_total"), thresholds=ZERO_GOOD,
              desc="Alertmanager couldn't deliver (e.g. mail server down). Alerts may have gone unseen."), 4),
        (stat("Alertmanager up", 'up{job="alertmanager"}', thresholds=[(None, "red"), (1, "green")]), 4),
        (stat("Rule failures (range)", total("prometheus_rule_evaluation_failures_total"), thresholds=ZERO_GOOD), 4),
    ], height=4)
    L.add([(table("Firing and pending alerts", [('ALERTS{alertstate=~"firing|pending"}', "")], join_on="alertname",
                  columns={"Value": ("Active", "short")}, extra_fields=("alertstate", "severity", "service", "instance"),
                  desc="Open http://127.0.0.1:9093 to silence an alert; each alert's runbook link is in its annotations."), 24)], height=8)
    L.row("History")
    L.add([
        (timeseries("Alerts by name", [('sum by (alertname, severity) (ALERTS{alertstate="firing"})', "{{alertname}} ({{severity}})")], "short", bars=True), 12),
        (timeseries("Notifications by integration", [
            (f"sum by (integration) (rate(alertmanager_notifications_total[{RI}]))", "{{integration}} sent"),
            (f"sum by (integration) (rate(alertmanager_notifications_failed_total[{RI}]))", "{{integration}} failed"),
        ], "ops"), 12),
    ])
    return dashboard("wispurl-alerting", "Alerting", "observability", "What is firing, what fired recently, and whether notifications are being delivered.", L)


ALL = [overview, business, service_detail, workers, host, containers, postgres, redis, rabbitmq, prometheus, loki, tempo, alloy, alerting]


def main() -> None:
    # Regenerate from scratch so a removed dashboard doesn't linger.
    for sub in [*FOLDERS, *FOLDERS.values()]:
        shutil.rmtree(OUT / sub, ignore_errors=True)
    for stale in OUT.glob("*.json"):
        stale.unlink()
    for build in ALL:
        folder, uid, dash = build()
        # The directory name becomes the Grafana folder name.
        path = OUT / FOLDERS[folder] / f"{uid}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(dash, indent=2, ensure_ascii=False) + "\n")
        print(f"wrote {path.relative_to(OUT.parent)}  ({len([p for p in dash['panels'] if p['type'] != 'row'])} panels)")


if __name__ == "__main__":
    main()
