---
id: local-018
title: ArgoCD local GitOps deployment
type: feat
feature: 9. Local Kubernetes and Packaging
status: not_started
depends_on: [local-016, local-017]
checklist_sections: 9. Local Kubernetes and Packaging; 4. Local CI/CD Pipeline
---

# ArgoCD local GitOps deployment

## Goal
Deploy ArgoCD into the Kind cluster and make version-controlled manifests/Helm values the source of truth for local application state.

## Implementation subtasks
- [ ] Pin ArgoCD chart/version
- [ ] define app projects and Applications for platform dependencies and WispURL services
- [ ] apply namespace boundaries and least-privilege RBAC
- [ ] configure sync ordering for Vault/secrets, data stores, observability, then applications
- [ ] set automated sync/prune only for safe namespaces and preserve stateful data
- [ ] provide an authenticated local UI access method
- [ ] test manual rollback by reverting a Git commit.

## Acceptance criteria
- [ ] Fresh cluster reaches Synced/Healthy from documented repository revision
- [ ] changing a test value is reconciled by ArgoCD
- [ ] unauthorized project cannot deploy cluster-wide resources
- [ ] rollback to prior Git revision restores previous image/config
- [ ] teardown does not accidentally delete persistent data without explicit action

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
