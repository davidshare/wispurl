---
id: LOC-3.03
title: "API/contract tests between services (e.g., Pact)"
category: "3. Testing"
status: todo
related:
  - docs/local/app/app-03-local-application-test-suite-and-coverage.md
---

# API/contract tests between services (e.g., Pact)

## What
Consumer-driven contracts keep service APIs from breaking their callers.

## Current state
None.

## Subtasks
- [ ] Pact consumer tests: gateway → auth, shortener, analytics, qr
- [ ] Pact consumer tests: shortener → analytics `/events`, shortener → rate-limiter `/check`
- [ ] Provider verification in each provider service
- [ ] Contract for the RabbitMQ event envelope
- [ ] Store pacts in-repo (or a local Pact Broker)

## Acceptance criteria
- [ ] A breaking provider change fails provider verification
