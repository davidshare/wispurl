---
id: local-038
title: Local threat model and security assumptions
type: feat
feature: 10. Security and Compliance
status: not_started
depends_on: []
checklist_sections: 10. Security and Compliance
---

# Local threat model and security assumptions

## Goal
Create a concise threat model for the current Docker/Kind architecture and record which controls are intentionally local-only.

## Implementation subtasks
- [ ] Identify internet-facing gateway/frontend, internal-only analytics/rate limiter, trust boundaries, Vault root/key storage, Docker socket mounted by Alloy, database/broker, CI secrets, image supply chain and developer workstation
- [ ] enumerate abuse cases and mitigations
- [ ] mark accepted risks and compensating controls
- [ ] add cloud transition notes for assumptions that must not carry over.

## Acceptance criteria
- [ ] Diagram and threat table cover each boundary and high-value secret
- [ ] every high risk has owner and mitigation or explicit acceptance
- [ ] Docker socket and local root-token storage are recorded
- [ ] assumptions are reviewed alongside architecture changes

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
