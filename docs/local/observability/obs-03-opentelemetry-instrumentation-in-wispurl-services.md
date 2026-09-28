---
id: local-024
title: OpenTelemetry instrumentation in WispURL services
type: feat
feature: 6. Observability
status: not_started
depends_on: [local-020, local-022, local-023]
checklist_sections: 6. Observability; 1. Application Foundations
---

# OpenTelemetry instrumentation in WispURL services

## Goal
Make traces and application metrics cross service boundaries for the actual WispURL request and event flows.

## Implementation subtasks
- [ ] Use shared/wispurl_otel consistently in gateway and each Python service
- [ ] assign stable service.name and environment/version attributes
- [ ] instrument inbound HTTP, outbound HTTP, PostgreSQL, Redis, RabbitMQ publish/consume
- [ ] propagate W3C trace context and baggage across HTTP and message headers
- [ ] configure OTLP export to Alloy with bounded batch, queue, timeout and sampling
- [ ] expose RED metrics on each service’s existing scrape endpoint
- [ ] never attach raw user IDs, short codes, auth headers or secret attributes
- [ ] ensure services start safely if the telemetry backend is temporarily unavailable.

## Acceptance criteria
- [ ] A browser/API request through gateway and two downstream services appears as one correlated Tempo trace
- [ ] a RabbitMQ analytics event has producer-consumer spans linked by context
- [ ] Prometheus shows request rate/errors/duration for every HTTP service
- [ ] trace labels contain no user secrets/high-cardinality IDs
- [ ] stopping Alloy does not crash the application and export resumes after recovery

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
