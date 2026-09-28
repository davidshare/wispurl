---
id: cloud-010
title: S3 backup and artifact buckets
type: feat
feature: 8. Backups and Disaster Recovery
status: not_started
depends_on: [cloud-001]
checklist_sections: 8. Backups and Disaster Recovery; 4. Cloud CI/CD
---

# S3 backup and artifact buckets

## Goal
Create private S3 locations for Terraform state, CI artifacts/SBOMs, and backups with separate access and lifecycle policies.

## Implementation subtasks
- [ ] Separate buckets or prefixes by purpose and access identity
- [ ] block public access
- [ ] enable encryption, versioning and access logging
- [ ] require TLS
- [ ] define lifecycle transition/expiration and noncurrent-version cleanup
- [ ] use Object Lock only if demonstrator budget/requirements justify
- [ ] restrict CI role to artifacts and backup role to backup prefix.

## Acceptance criteria
- [ ] Public access checks pass
- [ ] all buckets encrypt at rest and reject insecure transport
- [ ] intended role can write only its path
- [ ] lifecycle behavior tested on disposable objects
- [ ] backups and SBOMs are discoverable by commit/service
- [ ] monthly storage cost and retention are documented

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
