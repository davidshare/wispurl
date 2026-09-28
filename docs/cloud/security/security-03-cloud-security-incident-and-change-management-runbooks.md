---
id: cloud-022
title: Cloud security incident and change-management runbooks
type: feat
feature: 11. Security and Compliance
status: not_started
depends_on: [cloud-003, cloud-018]
checklist_sections: 11. Security and Compliance; 12. Operations
---

# Cloud security incident and change-management runbooks

## Goal
Document operational ownership, incident severity, break-glass, change approval, maintenance, and post-incident response for the AWS demonstrator.

## Implementation subtasks
- [ ] Define service owner for each app/platform component
- [ ] severity levels and response targets
- [ ] escalation/on-call simulation without paid paging requirement
- [ ] steps for leaked credential, suspicious secret read, compromised image, public exposure and AWS account lockout
- [ ] maintenance and change review windows
- [ ] blameless review template
- [ ] internal status page procedure.

## Acceptance criteria
- [ ] Tabletop exercise completes for leaked secret and compromised image
- [ ] responders can locate logs and revoke identity
- [ ] every service has named owner
- [ ] severity and escalation flow are unambiguous
- [ ] review template records timeline, impact, cause, corrective actions and owners

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
