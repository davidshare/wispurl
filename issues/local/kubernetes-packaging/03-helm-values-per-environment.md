---
id: LOC-9.03
title: "Helm values files separated for local, staging, and production"
category: "9. Local Kubernetes and Packaging"
status: todo
related:
  - docs/local/kubernetes/k8s-01-helm-packaging-for-wispurl-workloads.md
---

# Helm values files separated for local, staging, and production

## What
Values files are separated for local, staging and production.

## Current state
None.

## Subtasks
- [ ] `values.yaml` defaults
- [ ] `values-local.yaml`, `values-staging.yaml`, `values-production.yaml` (image, replicas, resources, ingress host, log level)
- [ ] No secrets in values files

## Acceptance criteria
- [ ] Rendering each environment produces the expected differences only
