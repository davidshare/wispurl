---
id: LOC-10.05
title: "Documented security assumptions"
category: "10. Security and Compliance (Local)"
status: todo
related:
  - docs/local/security/security-00-local-threat-model-and-security-assumptions.md
---

# Documented security assumptions

## What
Local-only security shortcuts are written down so they are not carried into the cloud.

## Current state
Partly scattered across the README.

## Subtasks
- [ ] Write `docs/security/assumptions.md` listing local-only choices: root token and unseal keys on disk, auto-unseal sidecar, self-signed CA, ports on all interfaces, superuser DSN for the exporter, shared HS256 JWT secret, Docker socket in Alloy
- [ ] For each: why it's acceptable locally, and what replaces it in the cloud

## Acceptance criteria
- [ ] Assumptions doc reviewed and linked from the README
