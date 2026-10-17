---
id: LOC-9.04
title: "Kustomize overlays or Helm environment management configured"
category: "9. Local Kubernetes and Packaging"
status: todo
related:
  - docs/local/kubernetes/k8s-01-helm-packaging-for-wispurl-workloads.md
---

# Kustomize overlays or Helm environment management configured

## What
One approach (Helm values per environment, or Kustomize overlays) manages environments without duplicated manifests.

## Current state
None.

## Subtasks
- [ ] Choose and document Helm-values-per-env vs Kustomize overlays (or Helm + Kustomize post-render)
- [ ] Wire environments into ArgoCD Applications/ApplicationSet

## Acceptance criteria
- [ ] Adding an environment needs only a new values/overlay file
