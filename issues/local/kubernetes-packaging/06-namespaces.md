---
id: LOC-9.06
title: "Kubernetes Namespaces defined and utilized"
category: "9. Local Kubernetes and Packaging"
status: todo
related:
  - docs/local/kubernetes/k8s-02-kind-manifests-and-workload-security-controls.md
---

# Kubernetes Namespaces defined and utilized

## What
Workloads are separated into purpose-specific namespaces.

## Current state
None.

## Subtasks
- [ ] Namespaces: `wispurl`, `wispurl-data` (if in-cluster), `observability`, `vault`, `argocd`, `ingress-nginx`
- [ ] Pod Security and ownership labels on each

## Acceptance criteria
- [ ] All workloads run outside `default`
