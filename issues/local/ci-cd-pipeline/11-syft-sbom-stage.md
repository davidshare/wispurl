---
id: LOC-4.11
title: "Pipeline stage: SBOM generation with Syft"
category: "4. Local CI/CD Pipeline (GitLab CI or Jenkins)"
status: todo
related:
  - docs/local/cicd/cicd-01-syft-sbom-generation-and-artifact-retention.md
---

# Pipeline stage: SBOM generation with Syft

## What
Generate an SBOM for every image.

## Current state
None.

## Subtasks
- [ ] `syft <image> -o spdx-json` and `-o cyclonedx-json`
- [ ] Store SBOMs as pipeline artifacts with a defined retention
- [ ] Name SBOMs by image digest

## Acceptance criteria
- [ ] Every pushed image has a matching SBOM artifact
