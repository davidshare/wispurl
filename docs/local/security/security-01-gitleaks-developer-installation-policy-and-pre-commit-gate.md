---
id: local-009
title: Gitleaks developer installation, policy, and pre-commit gate
type: feat
feature: 2. Secrets Management
status: not_started
depends_on: []
checklist_sections: 2. Secrets Management
---

# Gitleaks developer installation, policy, and pre-commit gate

## Goal
Provide reliable developer-side secret prevention using the repository’s .gitleaks.toml, .gitleaksignore, .pre-commit-config.yaml, and Makefile.

## Implementation subtasks
- [x] Pin the pre-commit Gitleaks hook to version 8.30.1
- [ ] Pin the standalone Gitleaks CLI version installed by the Makefile
- [x] make setup install or clearly diagnose missing tools on macOS and Linux
- [ ] ensure pre-commit scans staged content and blocks commit on a verified test secret
- [ ] make the ignore file require a reason and avoid broad suppressions
- [ ] document safe rotation/removal response
- [ ] scan current tracked tree and history as separate commands
- [ ] ensure report mode preserves scanner exit status or is explicitly non-gating and labeled.

## Acceptance criteria
- [ ] On a clean clone, documented setup installs the hook
- [ ] a synthetic canary secret staged in a disposable test file is blocked and then removed
- [ ] a clean staged change passes
- [ ] full-history scan returns failure on a test history fixture
- [ ] no allowlist hides project source/config paths broadly
- [ ] Make target output accurately describes current/history scan scope

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
