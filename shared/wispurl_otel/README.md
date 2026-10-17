# wispurl-otel

OpenTelemetry tracing shared by every WispURL Python service. It sends spans over OTLP to Grafana Alloy, which forwards them to Tempo.

## What it gives a service

| Function | What it does | Call it |
| --- | --- | --- |
| `setup_otel(service_name)` | Creates the tracer provider and OTLP exporter, and instruments outgoing `httpx` calls so trace context reaches the next service | Once, at process start, before creating httpx clients |
| `instrument_fastapi(app)` | One server span per incoming request; `/health`, `/ready`, `/live` and `/metrics` are skipped | After `app = FastAPI()` |
| `instrument_sqlalchemy(engine)` | One span per SQL statement | Right after `create_async_engine(...)` |
| `instrument_redis()` | One span per Redis command | Before creating Redis clients |
| `inject_trace_context(headers)` | Writes `traceparent` into RabbitMQ message headers | When publishing |
| `extract_trace_context(headers)` | Reads it back so the consumer span joins the producer's trace | When consuming |
| `add_trace_context` | structlog processor that adds `trace_id` and `span_id` to every log line | In the structlog processor chain |

## Configuration

Everything is read from standard OpenTelemetry environment variables (set in `docker-compose.yml` under `x-otel-env`):

| Variable | Example | Purpose |
| --- | --- | --- |
| `OTEL_SERVICE_NAME` | `shortener-service` | Name shown in Tempo and Grafana |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://alloy:4317` | Where spans go |
| `OTEL_EXPORTER_OTLP_TIMEOUT` | `10` | Export timeout, in **seconds** for the Python exporter |
| `OTEL_TRACES_SAMPLER` | `parentbased_always_on` | Sampling strategy |
| `OTEL_BSP_*` | `OTEL_BSP_MAX_QUEUE_SIZE=2048` | Batch size, delay and in-memory queue limit |
| `OTEL_RESOURCE_ATTRIBUTES` | `deployment.environment=local` | Extra attributes on every span |
| `OTEL_SDK_DISABLED` | `true` | Turns tracing off entirely |

If the collector is unreachable, spans are retried in the background and then dropped. Requests are never blocked.

## Silencing probes

Health checks that touch a dependency would otherwise create a trace every few seconds. Wrap them:

```python
from opentelemetry.instrumentation.utils import suppress_instrumentation

with suppress_instrumentation():
    await session.execute(text("SELECT 1"))
```
