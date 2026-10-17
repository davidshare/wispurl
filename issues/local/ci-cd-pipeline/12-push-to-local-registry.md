---
id: LOC-4.12
title: "Pipeline stage: push verified images to a local container registry (local Docker Registry or Harbor)"
category: "4. Local CI/CD Pipeline (GitLab CI or Jenkins)"
status: todo
related:
  - docs/local/containers/container-01-container-build-trivy-scan-and-local-registry-publishing.md
---

# Pipeline stage: push verified images to a local container registry (local Docker Registry or Harbor)

## What
Only scanned, verified images are pushed to a local registry the cluster pulls from.

## Current state
No local registry.

## Subtasks
- [ ] Run `registry:2` (or Harbor) on `localhost:5001` and connect it to the kind network
- [ ] Push only after all scan stages pass
- [ ] Record the pushed digest for deployment
- [ ] Configure registry garbage collection / retention

## Acceptance criteria
- [ ] The cluster pulls the image by the digest the pipeline produced
