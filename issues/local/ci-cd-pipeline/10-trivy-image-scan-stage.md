---
id: LOC-4.10
title: "Pipeline stage: container image vulnerability scanning with Trivy"
category: "4. Local CI/CD Pipeline (GitLab CI or Jenkins)"
status: todo
related:
  - docs/local/containers/container-01-container-build-trivy-scan-and-local-registry-publishing.md
---

# Pipeline stage: container image vulnerability scanning with Trivy

## What
Trivy scans each built image and blocks HIGH/CRITICAL vulnerabilities.

## Current state
None.

## Subtasks
- [ ] `trivy image --severity HIGH,CRITICAL --exit-code 1 --ignore-unfixed`
- [ ] Enable secret and misconfig scanners
- [ ] Maintain `.trivyignore` with justification
- [ ] Upload JSON/SARIF reports

## Acceptance criteria
- [ ] An image with a fixable critical CVE fails the stage
