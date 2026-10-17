---
id: local-031
title: Local database backup and restore
type: feat
feature: 8. Backups and Disaster Recovery
status: not_started
depends_on: []
checklist_sections: 8. Backups and Disaster Recovery
---

# Local database backup and restore

## Goal
Protect the three PostgreSQL databases with scheduled local pg_dump backups and prove recoverability.

## Implementation subtasks
- [ ] Back up auth_db, short_db and stats_db in a consistent format
- [ ] include roles/extensions or document recreation
- [ ] write timestamped compressed files to ignored backup directory
- [ ] enforce retention and disk cap
- [ ] verify exit status and nonempty file
- [ ] restore into a fresh isolated PostgreSQL volume and run integrity/smoke queries
- [ ] document local RPO/RTO targets and encryption if backup can contain sensitive local data.

## Acceptance criteria
- [ ] One command backs up all three databases and returns nonzero on any failure
- [ ] retention removes only expired generated backups
- [ ] restore drill recreates schema and representative records in an isolated instance
- [ ] runbook records backup duration, restore duration, measured RPO/RTO, and data-loss boundary

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
