---
id: LOC-9.11
title: "Liveness, Readiness, and Startup probes configured"
category: "9. Local Kubernetes and Packaging"
status: todo
related:
  - docs/local/kubernetes/k8s-02-kind-manifests-and-workload-security-controls.md
---

# Liveness, Readiness, and Startup probes configured

## What
Liveness, readiness and startup probes are configured for every workload.

## Current state
None (depends on `/live` and `/ready`).

## Subtasks
- [ ] Liveness → `/live`, readiness → `/ready`
- [ ] Startup probe for services that migrate on start
- [ ] Exec/heartbeat probes for workers

## Acceptance criteria
- [ ] Breaking a dependency removes pods from Service endpoints without restarting them
