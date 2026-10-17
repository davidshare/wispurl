---
id: LOC-2.14
title: "Gitleaks added as a blocking CI pipeline stage (see Section 3)"
category: "2. Secrets Management (Local)"
status: partial
related:
  - docs/local/security/security-04-blocking-gitleaks-ci-gate.md
---

# Gitleaks added as a **blocking** CI pipeline stage (see Section 3)

## What
Gitleaks runs in CI and a finding blocks merging.

## Current state
`.github/workflows/gitleaks.yml` runs on every push/PR with full history. Blocking depends on branch protection, which is not verified. `trufflehog.yaml:` has a trailing colon so GitHub never runs it.

## Subtasks
- [x] GitHub Actions workflow running gitleaks on push and PR
- [x] Full history checkout (`fetch-depth: 0`)
- [ ] Make the gitleaks job a required status check on `master`
- [ ] Pin actions by commit SHA
- [ ] Rename `.github/workflows/trufflehog.yaml:` → `trufflehog.yaml` (or remove it)
- [ ] Add the same gate to the local pipeline (see CI/CD)

## Acceptance criteria
- [ ] A PR containing a planted fake secret cannot be merged

## References
- [.github/workflows/gitleaks.yml](../../../.github/workflows/gitleaks.yml)
