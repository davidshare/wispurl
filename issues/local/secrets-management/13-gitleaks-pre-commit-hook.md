---
id: LOC-2.13
title: "Gitleaks wired in as a pre-commit hook, not just a manual/ad hoc scan"
category: "2. Secrets Management (Local)"
status: done
related:
  - docs/local/security/security-01-gitleaks-developer-installation-policy-and-pre-commit-gate.md
---

# Gitleaks wired in as a pre-commit hook, not just a manual/ad hoc scan

## What
Gitleaks runs automatically on every commit so secrets are blocked before they enter history.

## Current state
`.pre-commit-config.yaml` runs gitleaks v8.30.1; `make setup` installs gitleaks + pre-commit and wires the hook.

## Subtasks
- [x] pre-commit config with the gitleaks hook (pinned rev)
- [x] `make setup` installs tools and the hook
- [x] `make run-hooks` / `make update-hooks` helpers

## Acceptance criteria
- [x] Committing a fake key is blocked by the hook

## References
- [.pre-commit-config.yaml](../../../.pre-commit-config.yaml)
- [Makefile](../../../Makefile)
