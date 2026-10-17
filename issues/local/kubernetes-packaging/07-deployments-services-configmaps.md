---
id: LOC-9.07
title: "Kubernetes Deployments, Services, and ConfigMaps defined"
category: "9. Local Kubernetes and Packaging"
status: todo
related:
  - docs/local/kubernetes/k8s-02-kind-manifests-and-workload-security-controls.md
---

# Kubernetes Deployments, Services, and ConfigMaps defined

## What
Each service has a Deployment, Service and ConfigMap.

## Current state
None.

## Subtasks
- [ ] Deployment + ClusterIP Service for gateway, auth, shortener, analytics, qr, rate-limiter, frontend
- [ ] Deployments for analytics-consumer and notification (no Service)
- [ ] ConfigMaps for non-secret settings

## Acceptance criteria
- [ ] All services are Running and reachable via their Services
