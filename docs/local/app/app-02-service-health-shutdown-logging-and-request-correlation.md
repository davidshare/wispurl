---
id: local-004
title: Service health, shutdown, logging, and request correlation
type: feat
feature: 1. Application Foundations
status: not_started
depends_on: []
checklist_sections: 1. Application Foundations
---

# Service health, shutdown, logging, and request correlation

## Goal
Establish a consistent operational contract across all HTTP services, the analytics consumer, cleanup worker, and frontend.

## Implementation subtasks
- [ ] Define liveness, readiness, and startup semantics separately
- [ ] make readiness reflect required dependencies without turning liveness into a dependency check
- [ ] use one JSON log schema with timestamp, severity, service, environment, request/trace ID, and safe error fields
- [ ] accept or generate a request ID at the gateway and propagate it through HTTP and RabbitMQ message headers
- [ ] use context-local state rather than global mutable request state
- [ ] handle SIGTERM by stopping intake, finishing bounded in-flight work, closing DB/Redis/RabbitMQ connections, and exiting before Compose grace period
- [ ] publish API docs only for public HTTP APIs.

## Acceptance criteria
- [ ] Every service exposes the documented health semantics
- [ ] Compose healthchecks use readiness where dependency readiness is required
- [ ] a request through gateway to downstream logs carries one correlation ID
- [ ] a RabbitMQ event retains correlation metadata
- [ ] logs parse as JSON and contain no secrets
- [ ] SIGTERM exits cleanly within documented timeout
- [ ] OpenAPI is reachable for each public API and internal endpoints are not unintentionally exposed

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
