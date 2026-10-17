---
id: LOC-7.10
title: "Chaos test: dependency failures simulated and verified"
category: "7. Reliability and SRE (Local Validation)"
status: todo
related:
  - docs/local/sre/sre-03-local-failure-injection-and-chaos-validation.md
---

# Chaos test: dependency failures simulated and verified

## What
Dependency outages and latency behave as the degradation matrix says.

## Current state
None.

## Subtasks
- [ ] Stop Redis, RabbitMQ, Postgres, Vault and analytics one at a time
- [ ] Inject latency/packet loss with Toxiproxy
- [ ] Verify behaviour against the matrix and that alerts fire

## Acceptance criteria
- [ ] Observed behaviour matches the matrix for every dependency
