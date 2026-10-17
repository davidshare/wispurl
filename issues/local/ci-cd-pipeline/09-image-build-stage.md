---
id: LOC-4.09
title: "Pipeline stage: container image build, tagged with Git commit SHA"
category: "4. Local CI/CD Pipeline (GitLab CI or Jenkins)"
status: todo
related:
  - docs/local/containers/container-01-container-build-trivy-scan-and-local-registry-publishing.md
---

# Pipeline stage: container image build, tagged with Git commit SHA

## What
Build every service image and tag it with the Git commit SHA.

## Current state
Images are built ad hoc by `docker compose build` with no tags.

## Subtasks
- [ ] Build each service with buildx using registry/inline cache
- [ ] Tag `:<git-sha>` (immutable) and `:<branch>` (moving)
- [ ] Add OCI labels (`org.opencontainers.image.revision`, `source`, `created`)

## Acceptance criteria
- [ ] Each pipeline run produces images tagged with the commit SHA
