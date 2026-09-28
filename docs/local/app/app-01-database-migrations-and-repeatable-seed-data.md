---
id: local-005
title: Database migrations and repeatable seed data
type: feat
feature: 1. Application Foundations
status: not_started
depends_on: []
checklist_sections: 1. Application Foundations; 3. Testing
---

# Database migrations and repeatable seed data

## Goal
Make database schema setup reproducible and testable for the auth, shortener, and analytics databases.

## Implementation subtasks
- [ ] Use Alembic for each SQLAlchemy service that owns schema
- [ ] identify tables currently created through startup or init SQL and migrate them into versioned migrations
- [ ] keep db/init for database/user creation only
- [ ] seed only deterministic, non-secret development fixtures
- [ ] make initialization safe to repeat
- [ ] document upgrade and downgrade support and irreversible migration handling.

## Acceptance criteria
- [ ] A fresh database reaches current schema through documented migration commands
- [ ] a second run is a no-op
- [ ] upgrade and downgrade are verified on a disposable database
- [ ] migration failure leaves a clear diagnostic
- [ ] no production credentials or personal data are seeded
- [ ] each service’s schema ownership is documented

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
