---
id: LOC-4.14
title: "Pipeline stage: post-deployment smoke tests against local Kubernetes"
category: "4. Local CI/CD Pipeline (GitLab CI or Jenkins)"
status: todo
related:
  - docs/local/kubernetes/k8s-04-local-kubernetes-e2e-tests-and-smoke-checks.md
---

# Pipeline stage: post-deployment smoke tests against local Kubernetes

## What
After deploy, smoke tests verify the app and trigger a rollback when it is unhealthy.

## Current state
None.

## Subtasks
- [ ] Smoke script: `/ready` on each service + create-link → redirect via ingress
- [ ] On failure, run `argocd app rollback` (or `helm rollback`) and fail the pipeline
- [ ] Record the result as an artifact

## Acceptance criteria
- [ ] A deliberately broken release is detected and rolled back automatically
