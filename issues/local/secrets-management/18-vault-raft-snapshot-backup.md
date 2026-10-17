---
id: LOC-2.18
title: "Vault Raft snapshot backup configured (cross-ref Section 7)"
category: "2. Secrets Management (Local)"
status: done
related:
  - docs/local/security/security-02-local-vault-deployment-engines-identity-and-lifecycle.md
---

# Vault Raft snapshot backup configured (cross-ref Section 7)

## What
Vault state can be backed up as a Raft snapshot.

## Current state
`make vault-snapshot` saves a timestamped snapshot to `vault/snapshots/` (gitignored).

## Subtasks
- [x] `make vault-snapshot` target
- [x] Snapshots written to a host volume and gitignored

## Acceptance criteria
- [x] Running the target produces a `.snap` file

## Notes
- Scheduling and off-host copies are follow-ups; see [Backups](../backups-disaster-recovery/03-vault-raft-snapshots.md).

## References
- [Makefile](../../../Makefile)
