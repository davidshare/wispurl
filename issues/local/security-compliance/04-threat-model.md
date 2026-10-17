---
id: LOC-10.04
title: "Threat model drafted for the application architecture"
category: "10. Security and Compliance (Local)"
status: todo
related:
  - docs/local/security/security-00-local-threat-model-and-security-assumptions.md
---

# Threat model drafted for the application architecture

## What
A threat model covers the application architecture and its trust boundaries.

## Current state
Not started (local-038).

## Subtasks
- [ ] Architecture diagram with trust boundaries (internet → frontend/gateway, internal services, data stores, Vault, CI, developer machine)
- [ ] STRIDE table per boundary and high-value asset (Vault keys/root token, JWT secret, DB, Docker socket mounted into Alloy)
- [ ] Mitigation or explicit acceptance with an owner for each high risk
- [ ] Cloud transition notes

## Acceptance criteria
- [ ] Every boundary and high-value secret appears in the table with a mitigation or acceptance
