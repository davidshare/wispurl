---
title: "Observability for WispURL, Part 11: Connect Traces Across Services and Queues"
seo_title: "Trace Context Propagation over HTTP and RabbitMQ in Python"
slug: trace-context-propagation-http-rabbitmq-python
description: "Connect distributed traces across microservices: W3C traceparent over HTTP with httpx, and manual trace propagation through RabbitMQ headers."
series: "Observability for WispURL"
part: 11
date: 2026-10-17
last_updated: 2026-10-17
author: David Essien
tags: [opentelemetry, distributed-tracing, context-propagation, rabbitmq, httpx, python]
keywords:
  - "trace context propagation"
  - "W3C traceparent header"
  - "OpenTelemetry httpx instrumentation"
  - "RabbitMQ OpenTelemetry tracing"
  - "aio-pika trace propagation"
  - "producer consumer spans"
  - "distributed tracing microservices"
difficulty: advanced
estimated_time: 45 minutes
prerequisites:
  - "Part 10: Instrument Services with OpenTelemetry"
repo_files:
  - shared/wispurl_otel/src/wispurl_otel/instrumentation.py
  - shared/wispurl_otel/src/wispurl_otel/propagation.py
  - shortener-service/shared/messaging.py (and the three other copies)
  - analytics-service/app/worker.py
  - cleanup-service/app/main.py
  - notification-service/app/main.py
---

# Observability for WispURL, Part 11: Connect Traces Across Services and Queues

> **In short:** a trace only spans several services if each call carries the caller's trace context. For HTTP, instrument the client (`HTTPXClientInstrumentor`) so every outgoing request gets a W3C `traceparent` header, which the receiving service's FastAPI instrumentation reads and continues. For RabbitMQ, do it yourself: open a PRODUCER span when publishing, write `traceparent` into the message headers, and on the consumer side read it back and open a CONSUMER span with that context as its parent. Also initialise tracing in every worker process. One redirect then becomes one trace from the gateway, through the shortener and RabbitMQ, to the analytics consumer.

After Part 10, every service records spans, but each service's spans form their own trace. When the gateway calls the shortener, Tempo shows two unrelated traces. In this part you'll connect them, so one user request is one trace, end to end.

## Why traces break at service boundaries

Inside one process, OpenTelemetry tracks the **current span** in a context variable: any span started while another is active becomes its child. That only works within one process. When the gateway sends an HTTP request to the shortener, the shortener knows nothing about the gateway's span unless the request **tells** it.

Passing that information along is called **context propagation**. The caller **injects** the current trace context into the request, and the receiver **extracts** it and continues the trace.

## The W3C `traceparent` header

The standard format for trace context is the W3C Trace Context `traceparent` header:

```text
traceparent: 00-cf3af7bd0168bef62334f7ab4aeddd2c-b7ad6b7169203331-01
             │  │                                │                │
             │  trace ID (16 bytes, hex)         parent span ID   flags (01 = sampled)
             version
```

- The **trace ID** is the same for every span in the trace.
- The **parent span ID** is the caller's span; the receiver's first span becomes its child.
- The **sampled flag** carries the sampling decision from Part 10, so a `parentbased_` sampler downstream follows it.

`OTEL_PROPAGATORS=tracecontext,baggage` (Part 10) tells OpenTelemetry to use this format. **Baggage** is a companion header for passing arbitrary key-value pairs along a request; we enable it but don't use it yet.

## Design decisions

### Instrument HTTP clients, not every call site

The receiving side is already handled: FastAPI's instrumentation extracts `traceparent` from incoming requests. On the sending side, we instrument the **httpx library** once, so every request made by any httpx client gets the header automatically. Nobody has to remember to add it at each call site.

### Propagate through RabbitMQ by hand

Click events go from the shortener to the analytics consumer through RabbitMQ, so the HTTP mechanism doesn't apply. There is an OpenTelemetry package for aio-pika, but it wraps aio-pika's callback-based consumer API. WispURL's consumers read messages with `queue.iterator()`. With that style the package's span would cover only the moment a message is handed to the iterator, not the actual processing, so database calls made while handling the message wouldn't be part of it.

So we propagate manually, in WispURL's shared messaging module. It takes about 30 lines, and every behaviour is visible:

- the producer opens a **PRODUCER** span and writes `traceparent` into the message's headers;
- the consumer reads it back and opens a **CONSUMER** span with that context as its parent, around the whole processing of the message.

Message headers travel with the message through the broker, including through WispURL's retry republishing, so retries and dead-lettering stay part of the original trace.

### Trust at the edge

The gateway accepts `traceparent` from anyone on the internet, so a client can choose its own trace ID and force a trace to be sampled. That's convenient for debugging (you'll use it below) and harmless locally. On a public production edge, consider having the gateway ignore incoming trace context and always start a new trace, or rely on tail sampling (Part 10) so clients can't inflate trace volume.

## Step 1: Propagate over HTTP

The httpx instrumentation is part of `setup_otel` from Part 10:

```python
    # Adds a W3C `traceparent` header to every outgoing httpx request. The
    # receiving service's FastAPI instrumentation reads it and continues the
    # same trace, which is what connects spans across services.
    # The workers don't use httpx, so only instrument it where it's installed.
    if importlib.util.find_spec("httpx") is not None:
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

        HTTPXClientInstrumentor().instrument()
```

> `shared/wispurl_otel/src/wispurl_otel/instrumentation.py` lines 53–60.

`HTTPXClientInstrumentor().instrument()` patches httpx globally. From then on, every request:

1. opens a **CLIENT** span (named after the method, such as `GET`, with the URL and status as attributes);
2. injects `traceparent` with that client span's ID into the request headers.

**It must run before any httpx client is created.** The gateway and shortener each create one shared `httpx.AsyncClient` in their FastAPI lifespan. Because `setup_otel` runs at module import, long before the lifespan starts, those clients are instrumented. A client created earlier would silently produce no spans and no headers.

`importlib.util.find_spec("httpx")` checks whether httpx is installed without importing it, so the queue workers, which don't use httpx, skip this step instead of crashing.

The package is listed in `shared/wispurl_otel/pyproject.toml` as `opentelemetry-instrumentation-httpx`.

## Step 2: Helpers for message headers

`shared/wispurl_otel/src/wispurl_otel/propagation.py` wraps OpenTelemetry's propagation API for AMQP headers:

```python
class _HeaderGetter(Getter[Mapping[str, Any]]):
    """Read AMQP header values, which may arrive as bytes, as strings."""

    def get(self, carrier: Mapping[str, Any], key: str) -> list[str] | None:
        value = carrier.get(key)
        if value is None:
            return None
        if isinstance(value, bytes):
            value = value.decode("utf-8", errors="replace")
        return [str(value)]

    def keys(self, carrier: Mapping[str, Any]) -> list[str]:
        return list(carrier.keys())


_getter = _HeaderGetter()


def inject_trace_context(headers: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    """Add the current trace context (traceparent, tracestate) to ``headers``."""
    carrier: dict[str, str] = {}
    propagate.inject(carrier)
    headers.update(carrier)
    return headers


def extract_trace_context(headers: Mapping[str, Any] | None) -> Context:
    """Return the trace context stored in message headers (empty if absent)."""
    return propagate.extract(headers or {}, getter=_getter)
```

> `propagation.py` lines 18–46.

- **`propagate.inject(carrier)`** writes the current context into a dictionary using the configured propagators, producing `{"traceparent": "00-…-…-01"}`. We merge that into the message headers.
- **`propagate.extract(headers, getter=...)`** does the reverse and returns a `Context` object holding the remote parent span.
- **The custom getter** exists because AMQP header values can come back from the broker as `bytes` rather than `str`, depending on how they were encoded. The default getter would fail to parse those; ours decodes them first.
- **No `traceparent` header** (for example, a message published by an older version) gives an empty context, and the consumer simply starts a new trace.

The functions are exported from the package (`from wispurl_otel import inject_trace_context, extract_trace_context`), so the messaging code stays free of OpenTelemetry details.

## Step 3: Producer spans

WispURL's services share one messaging module, copied into each service's `shared/messaging.py`. It gets a tracer at the top:

```python
from opentelemetry import trace
from opentelemetry.trace import SpanKind
from wispurl_otel import extract_trace_context, inject_trace_context

tracer = trace.get_tracer(__name__)
```

> `shortener-service/shared/messaging.py` lines 40–46.

The publish method wraps sending in a PRODUCER span and injects its context into the headers:

```python
    async def publish(self, envelope: EventEnvelope, *, routing_key: str) -> None:
        """Publish ``envelope`` under ``routing_key`` (awaits the broker confirm)."""
        # A PRODUCER span for the publish; its context travels in the headers so
        # the consumer's span joins the same trace.
        with tracer.start_as_current_span(
            f"{routing_key} publish",
            kind=SpanKind.PRODUCER,
            attributes={
                "messaging.system": "rabbitmq",
                "messaging.operation.type": "send",
                "messaging.destination.name": EXCHANGE_NAME,
                "messaging.rabbitmq.destination.routing_key": routing_key,
            },
        ):
            headers: dict[str, Any] = {
                "x-attempt": 1,
                "x-request-id": envelope.request_id or "",
            }
            inject_trace_context(headers)
            message = Message(
                body=envelope.model_dump_json().encode("utf-8"),
                delivery_mode=DeliveryMode.PERSISTENT,
                content_type="application/json",
                headers=headers,
            )
            await self._exchange.publish(message, routing_key=routing_key)
```

> `messaging.py` lines 147–172.

- **The span name** follows OpenTelemetry's messaging conventions, `<destination> <operation>`, such as `link.clicked publish`.
- **`SpanKind.PRODUCER`** tells Tempo this span hands work to someone else asynchronously. Tempo's service graph (Part 9) uses PRODUCER/CONSUMER pairs to draw the edge from the shortener to the analytics consumer, as well as CLIENT/SERVER pairs.
- **The attributes** use OpenTelemetry's standard messaging attribute names, so tools that know the conventions can interpret them.
- **`inject_trace_context` runs inside the span**, so the context written into the headers is the PRODUCER span's. The consumer becomes its child.
- The existing `x-request-id` header still travels alongside: the request ID links logs (Part 8); the trace context links spans.

## Step 4: Consumer spans

Each message is handled by `_process_message`. It now opens a CONSUMER span, parented on the context from the headers, around all of the processing:

```python
    bind_request_id(_header_str(message, "x-request-id"))
    # A CONSUMER span whose parent is the producer's span, read from the
    # message headers. Without this the consumer would start a new trace.
    with tracer.start_as_current_span(
        f"{queue_name} process",
        context=extract_trace_context(message.headers),
        kind=SpanKind.CONSUMER,
        attributes={
            "messaging.system": "rabbitmq",
            "messaging.operation.type": "process",
            "messaging.destination.name": queue_name,
        },
    ) as span:
        try:
            try:
                envelope = EventEnvelope.model_validate_json(message.body)
            except ValidationError as exc:
                # ... malformed: dead-letter and ack
            attempt = _header_int(message, "x-attempt", 1)
            try:
                await handler(envelope)
                await message.ack()
            except Exception as exc:  # noqa: BLE001 - bounded retry, then dead-letter
                span.record_exception(exc)
                # ... retry or dead-letter as before
```

> `messaging.py` lines 250–277 onward.

- **`context=extract_trace_context(...)`** is the key line: the new span's parent is the producer's span from another process, delivered by RabbitMQ.
- **Everything the handler does happens inside the span.** The analytics consumer's database inserts (Part 12) and any milestone events it publishes become children of this span, all in the original trace.
- **`span.record_exception(exc)`** attaches the error and its stack trace to the span when processing fails. In Tempo you see the failure in the trace, followed by the retry: the retry republishes the message with its original headers, so it carries the same trace context.

`messaging.py` is identical in the shortener, analytics, cleanup and notification services, so the same change goes into all four copies.

## Step 5: Initialise tracing in the workers

The three queue workers (analytics consumer, cleanup, notification) aren't web apps, so nothing called `setup_otel` for them in Part 10. Without it, OpenTelemetry's API falls back to a no-op tracer: the spans in `messaging.py` would be created and silently discarded.

Each worker calls it at the start of its `main()`:

```python
    setup_otel(service_name=os.getenv("OTEL_SERVICE_NAME", "notification-service"))
```

> `notification-service/app/main.py` line 30; `analytics-service/app/worker.py` line 44; `cleanup-service/app/main.py` line 55.

Their Compose definitions already merge `*otel-env` and set `OTEL_SERVICE_NAME`, so they export to Alloy like the HTTP services. Cleanup and notification also need `wispurl-otel` in their `pyproject.toml`.

### A root span for scheduled work

The cleanup worker isn't triggered by a request or a message: it wakes up every minute and sweeps expired links. Without a span around each sweep, its database queries and published events would each start their own one-span trace. So each sweep gets a root span:

```python
tracer = trace.get_tracer(__name__)
# ...
                    # One trace per sweep: its SQL and publish spans nest under it.
                    with tracer.start_as_current_span("cleanup sweep"):
                        await run_once(publisher, settings.batch_size)
```

> `cleanup-service/app/main.py` lines 27 and 71–73.

Now each sweep is one trace. Its `link.expired publish` spans connect to the notification worker's processing of those events, so you can follow an expiry all the way to the notification.

Rebuild everything to apply the changes:

```sh
docker compose up --build -d
```

## Check that it works

**Follow one request from outside.** Choose your own trace ID, send it in a `traceparent` header, and look it up. Replace `<short-code>` with one of your links:

```sh
TID=$(python3 -c 'import os; print(os.urandom(16).hex())')
SID=$(python3 -c 'import os; print(os.urandom(8).hex())')
curl -s -o /dev/null -w '%{http_code}\n' -H "traceparent: 00-$TID-$SID-01" http://localhost:8080/<short-code>
echo "$TID"
```

After about 10 seconds, open Grafana → Explore → Tempo, choose **Search** → **TraceQL**, paste the trace ID, and run it. You'll see one trace containing:

```text
gateway                     SERVER    GET /{short_code}
gateway                     CLIENT    GET
shortener-service           SERVER    GET /{short_code}
shortener-service           CLIENT    SELECT short_db
shortener-service           PRODUCER  link.clicked publish
analytics-consumer-service  CONSUMER  analytics.clicks process
analytics-consumer-service  CLIENT    INSERT stats_db
```

Three services, two transport hops (HTTP and RabbitMQ), one trace, under the ID **you** chose. (The SQL spans come from Part 12.)

Look at the timeline: the analytics consumer's spans start **after** the gateway has already responded. The redirect didn't wait for analytics; the click was recorded asynchronously. That's the architecture working as designed, and the trace makes it visible.

**Link creation spans three services too:**

```traceql
{ resource.service.name = "gateway" && name = "POST /v1/links" }
```

Open a result: gateway → shortener → rate limiter, with the rate limiter's Redis call inside.

**Look at the service map.** In Explore → Tempo, choose the **Service Graph** query type. After a few minutes of traffic you'll see edges like these (they're also in Prometheus as `traces_service_graph_request_total{client, server}`):

```text
user                       → gateway
gateway                    → auth-service, shortener-service
shortener-service          → rate-limiter-service, analytics-consumer-service, short_db
rate-limiter-service       → redis
analytics-consumer-service → stats_db
cleanup-service            → short_db
```

The edge from the shortener to the analytics consumer comes from the PRODUCER/CONSUMER spans: RabbitMQ never appears as a hop, because the service graph links the publishing service to the consuming one. Databases and Redis show up as their own nodes, built from the CLIENT spans added in Part 12. `user` stands for "whoever called the first service", here the browser or `curl`.

**A cleanup sweep is one trace:**

```traceql
{ name = "cleanup sweep" }
```

## When something goes wrong

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Gateway and shortener spans in separate traces | httpx not instrumented, or the client was created before `setup_otel` ran | Call `setup_otel` at import time, before any `httpx.AsyncClient` is created. |
| Consumer spans in their own trace | `traceparent` missing from message headers, or not extracted | Inject inside the PRODUCER span; pass `context=extract_trace_context(message.headers)` to the CONSUMER span. |
| Worker spans never appear | `setup_otel` not called in the worker | Call it at the start of the worker's `main()`. |
| Extraction fails silently | Header values arrived as bytes | Use a getter that decodes bytes, as `_HeaderGetter` does. |
| Consumer span too short to contain the work | The consumer span wraps only message delivery | Open the span around the full handling of the message, as in Step 4. |
| Cleanup produces many one-span traces | No root span around scheduled work | Wrap each run in `tracer.start_as_current_span(...)`. |

## What you have now

- Trace context travelling over HTTP automatically, via instrumented httpx clients.
- Trace context travelling through RabbitMQ, with PRODUCER and CONSUMER spans and failures recorded.
- Tracing in every process, including the three workers, with a root span for scheduled sweeps.
- End-to-end traces: one request, one trace, across services and the message queue.

In [Part 12](12-trace-database-and-redis-calls.md) we add a span for every SQL query and Redis command, and keep health-check noise out of traces.

## Key takeaways

- A trace crosses process boundaries only if the trace context is injected by the caller and extracted by the receiver.
- Use the W3C `traceparent` header; its sampled flag carries the sampling decision downstream.
- Instrument HTTP client libraries once, before clients are created, instead of adding headers at each call site.
- For message queues, open a PRODUCER span and inject into message headers; open a CONSUMER span around the whole handling of the message, parented on the extracted context.
- Every process needs its own tracing setup, including background workers. Give scheduled jobs a root span.
- Decide whether your public edge should trust incoming trace context.

## FAQ

### What is trace context propagation?

Passing a trace's identity (trace ID, parent span ID and sampling flag) from one service to the next with each call, so the receiving service's spans join the same trace. Over HTTP this uses the W3C `traceparent` header; over message queues it uses message headers.

### What is the traceparent header?

A W3C standard HTTP header in the form `version-traceid-parentid-flags`, for example `00-cf3af7bd0168bef62334f7ab4aeddd2c-b7ad6b7169203331-01`. OpenTelemetry writes it on outgoing requests and reads it on incoming ones.

### How do I propagate OpenTelemetry trace context through RabbitMQ?

When publishing, start a PRODUCER span and call `opentelemetry.propagate.inject()` on a dictionary that you merge into the message headers. When consuming, call `propagate.extract()` on the message headers and pass the result as `context=` when starting a CONSUMER span around the message handling.

### Why are my traces split into several traces per request?

Usually because one hop doesn't propagate context: an HTTP client that isn't instrumented (or was created before instrumentation ran), a message queue without header propagation, or a process that never initialised tracing. Look for the service where the trace breaks and check that hop.

### Should the API gateway accept traceparent headers from clients?

It's convenient for debugging, but it lets clients choose trace IDs and force sampling. On a public production edge, many teams start a fresh trace at the gateway, or use tail sampling so client-provided flags can't increase trace volume.

---

**Series navigation:** Previous: [Part 10, Instrument Services with OpenTelemetry](10-instrument-services-with-opentelemetry.md) · [Series index](README.md) · Next: [Part 12, Trace Database and Redis Calls](12-trace-database-and-redis-calls.md)
