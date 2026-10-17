---
id: LOC-2.01
title: "Gitleaks installed and actively scanning the repo for committed secrets"
category: "2. Secrets Management (Local)"
status: done
related:
  - docs/local/security/security-01-gitleaks-developer-installation-policy-and-pre-commit-gate.md
---

# Gitleaks installed and actively scanning the repo for committed secrets

## What
Gitleaks scans the working tree and full history for committed secrets using a project-tuned config.

## Current state
`make install-gitleaks`, `make scan`, `make scan-report`, `make scan-staged`; `.gitleaks.toml` extends defaults with DB-URL, JWT-secret and PEM rules; `.gitleaksignore` documents the fingerprint process.

## Subtasks
- [x] Install target for macOS/Linux with guidance for Windows
- [x] Full-history scan target and JSON report target
- [x] Custom rules and allowlists in `.gitleaks.toml`
- [x] `.gitleaksignore` with documented usage

## Acceptance criteria
- [x] `make scan` completes with no findings on the current history

## References
- [Makefile](../../../Makefile)
- [.gitleaks.toml](../../../.gitleaks.toml)
- [.gitleaksignore](../../../.gitleaksignore)
