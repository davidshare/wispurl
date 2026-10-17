---
id: LOC-2.16
title: "Verified no secrets get baked into Docker images (docker history, layer inspection)"
category: "2. Secrets Management (Local)"
status: partial
related:
  - docs/local/security/security-02-local-vault-deployment-engines-identity-and-lifecycle.md
---

# Verified no secrets get baked into Docker images (`docker history`, layer inspection)

## What
Images are verified not to contain secrets in any layer.

## Current state
Dockerfiles copy explicit directories (not `COPY . .`), so `.env` is not copied today, but `.dockerignore` files don't exclude `.env`, and no image has been inspected.

## Subtasks
- [x] Dockerfiles copy only explicit paths
- [ ] Add `.env*`, `*.pem`, `*.key` and `vault/` to every `.dockerignore`
- [ ] Build all images and inspect with `docker history --no-trunc` and `dive`
- [ ] Run `trivy image --scanners secret` against every image
- [ ] Add the image secret scan to CI

## Acceptance criteria
- [ ] Every image passes a secret scan, with evidence recorded

## References
- [auth-service/.dockerignore](../../../auth-service/.dockerignore)
