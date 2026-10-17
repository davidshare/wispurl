---
id: local-006
title: Dependency lockfiles and reproducible installs
type: feat
feature: 1. Application Foundations
status: not_started
depends_on: []
checklist_sections: 1. Application Foundations
---

# Dependency lockfiles and reproducible installs

## Goal
Make Python and frontend dependency resolution deterministic across all independently built services.

## Implementation subtasks
- [ ] Verify each Python service and shared package has a committed uv lockfile consistent with pyproject constraints
- [ ] use locked/sync install mode in Docker builds and CI
- [ ] pin Node runtime and install frontend dependencies from package-lock
- [ ] define an intentional dependency update process
- [ ] remove unbounded direct dependency ranges where they defeat reproducibility while retaining compatible security updates.

## Acceptance criteria
- [ ] A clean install for each service and frontend succeeds in locked mode
- [ ] lockfile drift fails CI
- [ ] Docker builds do not resolve a new dependency graph unexpectedly
- [ ] supported runtime versions are documented
- [ ] all services and shared modules are included in the dependency inventory

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
