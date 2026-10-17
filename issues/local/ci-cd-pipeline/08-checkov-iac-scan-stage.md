---
id: LOC-4.08
title: "Pipeline stage: filesystem/IaC scanning with Checkov"
category: "4. Local CI/CD Pipeline (GitLab CI or Jenkins)"
status: todo
related:
  - docs/local/security/security-06-checkov-infrastructure-and-configuration-gate.md
---

# Pipeline stage: filesystem/IaC scanning with Checkov

## What
Checkov scans Dockerfiles, Compose/Kubernetes/Helm config and CI definitions for misconfigurations.

## Current state
None.

## Subtasks
- [ ] Run `checkov -d .` with Dockerfile, Kubernetes, Helm, GitHub Actions and secrets frameworks
- [ ] Keep a skip list with a written justification per check
- [ ] Fail on high severity

## Acceptance criteria
- [ ] A container running as root or a missing resource limit fails the stage
