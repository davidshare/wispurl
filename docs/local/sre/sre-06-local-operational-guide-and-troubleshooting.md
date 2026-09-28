---
id: local-037
title: Local operational guide and troubleshooting
type: feat
feature: 11. Operations and Incident Response
status: not_started
depends_on: [local-001, local-010]
checklist_sections: 11. Operations and Incident Response
---

# Local operational guide and troubleshooting

## Goal
Consolidate local developer operating procedures so the project can be started, inspected, updated, rolled back, and cleaned without tribal knowledge.

## Implementation subtasks
- [ ] Document prerequisites and versions
- [ ] initial environment setup
- [ ] Compose and observability start order
- [ ] readiness checks
- [ ] logs and common failure signatures
- [ ] database migration/seed commands
- [ ] CI and local act commands
- [ ] Kind/ArgoCD deploy and rollback
- [ ] Vault access/rotation
- [ ] port map
- [ ] cleanup choices
- [ ] explain which commands delete persistent state.

## Acceptance criteria
- [ ] A new contributor follows guide from clean checkout through a successful user journey
- [ ] troubleshooting section resolves at least missing env, unhealthy dependency, Vault sealed, telemetry target down, and failed ArgoCD sync
- [ ] destructive commands require explicit confirmation flags or clear warnings
- [ ] documentation has no stale paths or fictitious targets

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
