---
id: local-015
title: Syft SBOM generation and artifact retention
type: feat
feature: 4. Local CI/CD Pipeline
status: not_started
depends_on: [local-010, local-014]
checklist_sections: 4. Local CI/CD Pipeline
---

# Syft SBOM generation and artifact retention

## Goal
Generate a useful, traceable SBOM for every WispURL application image with Syft and retain it with the build artifacts.

## Implementation subtasks
- [ ] Generate both SPDX JSON and CycloneDX JSON for each commit-SHA image: auth-service, shortener-service, analytics-service, analytics-consumer-service, cleanup-service, notification-service, rate-limiter-service, QR service, gateway, frontend, and Vault
- [ ] include OS packages and application dependencies
- [ ] generate after image build and before publication
- [ ] name artifacts by service, image digest, and commit
- [ ] retain downloadable artifacts for 30 days in CI and publish beside images in the local registry metadata where supported
- [ ] do not claim an SBOM is a vulnerability scan
- [ ] fail the job if any expected image is missing or Syft exits unsuccessfully.

## Acceptance criteria
- [ ] One SPDX and one CycloneDX document exist for every expected image
- [ ] documents parse and include package name/version plus image identity
- [ ] expected Python and Node runtime dependencies appear
- [ ] artifact names resolve to the exact image digest and commit
- [ ] deliberately failing Syft invocation fails the job
- [ ] missing one service SBOM fails the job

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
