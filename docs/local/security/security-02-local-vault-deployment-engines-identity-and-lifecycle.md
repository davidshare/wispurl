---
id: local-007
title: Local Vault deployment, engines, identity, and lifecycle
type: feat
feature: 2. Secrets Management
status: verify
depends_on: []
checklist_sections: 2. Secrets Management; 8. Backups and Disaster Recovery; 11. Operations
---

# Local Vault deployment, engines, identity, and lifecycle

## Goal
Deliver one complete, secure local Vault lifecycle using the existing Raft/TLS Compose service, initialization sidecar, bootstrap scripts, and Make targets.

## Implementation subtasks
- [ ] Pin the Vault image and document supported version
- [ ] generate TLS certs with SANs for host and Docker names
- [x] configure the initializer for five key shares and a threshold of three
- [x] ensure key JSON is mode 0600 under ignored vault/keys and never printed to logs
- [ ] document offline distribution and production KMS auto-unseal model
- [ ] bootstrap file audit device and prove events persist
- [x] configure bootstrap to enable KV v2 and create one least-privilege policy/AppRole per service identity
- [ ] verify paths and secret field names against every service setting
- [ ] configure PostgreSQL dynamic DB credentials with separate least-privilege roles for auth_db, short_db, stats_db and bounded leases
- [ ] explicitly assess Transit and PKI use cases and enable only if a project need is documented
- [ ] test Vault Agent authentication/template delivery with auth-service
- [ ] define and execute a secret rotation
- [ ] keep Raft snapshots on the host, document retention, and complete a restore drill in disposable state
- [ ] fix lifecycle/documentation mismatches including vault-clean behavior, snapshot paths, and key path.

## Acceptance criteria
- [ ] Fresh Vault initializes and unseals without manual root-token exposure
- [ ] restarting sealed Vault unseals only from protected local key material
- [ ] each service role reads only its own KV path and cannot list/read another service path or administer Vault
- [ ] audit events show denied and allowed reads
- [ ] dynamic DB credentials connect only to their assigned DB and expire/revoke
- [ ] rotation succeeds without leaving old credential valid beyond its lease
- [ ] Vault Agent test delivers a secret without putting it in an image
- [ ] snapshot restore recovers known test data
- [ ] cleanup command effects match its help text
- [ ] developer setup and production unseal guidance are documented

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
