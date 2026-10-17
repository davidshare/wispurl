---
id: LOC-5.06
title: "CPU and memory limits defined in Compose and Kubernetes manifests"
category: "5. Container Security (Local)"
status: todo
related:
  - docs/local/containers/container-00-multi-stage-application-images-and-runtime-hardening.md
---

# CPU and memory limits defined in Compose and Kubernetes manifests

## What
Every container has CPU and memory limits in Compose and Kubernetes.

## Current state
No limits are defined (`deploy:` appears only commented out).

## Subtasks
- [ ] Measure baseline usage with `docker stats` under light load
- [ ] Add `deploy.resources.limits` and `reservations` for every app, data-store and observability service
- [ ] Mirror them as `resources.requests/limits` in Helm values

## Acceptance criteria
- [ ] No container is unbounded, and the stack still runs under the load test

## Notes
- Overlaps with [Requests and limits](../kubernetes-packaging/10-resource-requests-limits.md) and [Cost & capacity](../cost-capacity/01-resource-limits-budget.md).
