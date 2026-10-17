---
id: LOC-7.09
title: "Chaos test: service restarts simulated and verified"
category: "7. Reliability and SRE (Local Validation)"
status: todo
related:
  - docs/local/sre/sre-03-local-failure-injection-and-chaos-validation.md
---

# Chaos test: service restarts simulated and verified

## What
Killing and restarting services under load is survivable and recovery time is measured.

## Current state
None.

## Subtasks
- [ ] Script restarts/kills of each service while k6 runs (`docker compose kill/restart`, later `kubectl delete pod`)
- [ ] Measure error spike and time to recovery
- [ ] Record results and fixes

## Acceptance criteria
- [ ] Each service recovers without manual action, with results recorded
