---
id: LOC-10.02
title: "Network segmentation / default-deny NetworkPolicies applied"
category: "10. Security and Compliance (Local)"
status: todo
related:
  - docs/local/kubernetes/k8s-02-kind-manifests-and-workload-security-controls.md
---

# Network segmentation / default-deny NetworkPolicies applied

## What
Network access is segmented so components reach only what they need.

## Current state
Every Compose service shares one `wispurl-network` (the frontend can reach Postgres and Vault).

## Subtasks
- [ ] Split Compose networks: `edge` (frontend, gateway), `app` (services), `data` (Postgres, Redis, RabbitMQ), `vault`
- [ ] Attach each service only to the networks it needs
- [ ] Apply default-deny NetworkPolicies in Kubernetes

## Acceptance criteria
- [ ] Frontend → Postgres connection fails, and the app still works
