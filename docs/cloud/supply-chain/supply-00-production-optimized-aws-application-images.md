---
id: cloud-027
title: Production-optimized AWS application images
type: feat
feature: 1. Application Foundations
status: not_started
depends_on: [cloud-011]
checklist_sections: 1. Application Foundations; 5. Container Security
---

# Production-optimized AWS application images

## Goal
Create cloud release images that retain local development convenience while removing debug tooling, build dependencies, and development-only configuration.

## Implementation subtasks
- [ ] Build each of the ten application images from locked dependencies in a multi-stage build
- [ ] include only runtime libraries and required CA certificates
- [ ] use pinned non-root runtime bases
- [ ] exclude source-control metadata, test fixtures, local env files and build secrets
- [ ] tag with commit and immutable digest
- [ ] record image-size baseline and document any runtime tool exception.

## Acceptance criteria
- [ ] All cloud release images build in CI
- [ ] final stages contain no compiler or development dependency unless justified
- [ ] layer inspection finds no env files, credentials or test fixtures
- [ ] each runs as non-root
- [ ] image digest is immutable and Trivy scan passes configured threshold

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
