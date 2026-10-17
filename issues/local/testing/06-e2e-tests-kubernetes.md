---
id: LOC-3.06
title: "End-to-end (E2E) tests running against the local Kubernetes cluster"
category: "3. Testing"
status: todo
related:
  - docs/local/kubernetes/k8s-04-local-kubernetes-e2e-tests-and-smoke-checks.md
---

# End-to-end (E2E) tests running against the local Kubernetes cluster

## What
End-to-end tests run against the app deployed in the local Kubernetes cluster.

## Current state
No cluster yet.

## Subtasks
- [ ] Write E2E tests (pytest + httpx or Playwright) targeting the ingress host
- [ ] Cover signup → create link → redirect → analytics visible
- [ ] Run after each ArgoCD/Helm deploy in the pipeline

## Acceptance criteria
- [ ] E2E suite passes against kind after a fresh deploy
