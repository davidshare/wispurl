---
id: LOC-9.02
title: "Helm charts created for all application services"
category: "9. Local Kubernetes and Packaging"
status: todo
related:
  - docs/local/kubernetes/k8s-01-helm-packaging-for-wispurl-workloads.md
---

# Helm charts created for all application services

## What
Helm charts package every application service.

## Current state
None.

## Subtasks
- [ ] Create a shared library chart (deployment, service, configmap, serviceaccount, hpa, pdb, networkpolicy templates)
- [ ] Per-service charts or an umbrella chart covering gateway, auth, shortener, analytics, analytics-consumer, qr, rate-limiter, notification, cleanup and frontend
- [ ] `helm lint` and `helm template` in CI

## Acceptance criteria
- [ ] `helm install` deploys all services to kind
