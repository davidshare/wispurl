---
id: LOC-10.01
title: "RBAC and least privilege enforced in local cluster"
category: "10. Security and Compliance (Local)"
status: partial
related:
  - docs/local/kubernetes/k8s-02-kind-manifests-and-workload-security-controls.md
---

# RBAC and least privilege enforced in local cluster

## What
Least privilege is enforced and verified across the cluster and Vault.

## Current state
Vault policies are per-service (done). Each service connects to PostgreSQL with its own least-privilege login instead of the superuser (done). There's no cluster yet.

## Subtasks
- [x] Per-service PostgreSQL logins: each owns only its own database, other databases refuse it, cleanup has column-level grants only (`db/init/create-service-roles.sh`, shortener migration `20261017_0003`)
- [ ] Apply ServiceAccount/RBAC work from Kubernetes
- [ ] Audit with `kubectl auth can-i --list` per ServiceAccount and Kubescape RBAC controls
- [ ] Define developer/operator roles (read-only vs admin)
- [ ] Replace root-token use in `make vault-env` with a developer policy

## Acceptance criteria
- [ ] An RBAC review shows no over-privileged subjects
