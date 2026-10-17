---
id: local-026
title: Local application test suite and coverage
type: feat
feature: 3. Testing
status: not_started
depends_on: []
checklist_sections: 3. Testing; 4. Local CI/CD Pipeline
---

# Local application test suite and coverage

## Goal
Make automated tests cover the service boundaries and local dependencies, with predictable Compose execution and reportable coverage.

## Implementation subtasks
- [ ] Define one command per Python service using uv locked environments and one frontend test/build command
- [ ] include unit tests, service integration tests against PostgreSQL/Redis/RabbitMQ containers, consumer-driven Pact contracts for gateway calls to auth, shortener, analytics and QR APIs, provider verification in each service, Alembic upgrade/downgrade tests on disposable DBs, and API smoke checks
- [ ] publish JUnit and coverage reports in CI
- [ ] set a baseline threshold per service and fail only on new/changed code below policy
- [ ] keep test secrets and fixture data fake.

## Acceptance criteria
- [ ] All tests run from clean checkout with documented Compose dependencies
- [ ] reports are collected by CI
- [ ] migration tests start from empty DB and verify downgrade
- [ ] each consumer contract is verified by its provider and a deliberately changed response field fails verification
- [ ] service integration tests fail clearly when dependency is unavailable
- [ ] coverage threshold is explicit and enforced

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
