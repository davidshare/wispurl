---
id: cloud-013
title: Cloud SBOM, image signing, ECR publication, and admission verification
type: feat
feature: 4. Cloud CI/CD
status: not_started
depends_on: [cloud-004, cloud-011]
checklist_sections: 4. Cloud CI/CD; 5. Container Security
---

# Cloud SBOM, image signing, ECR publication, and admission verification

## Goal
Create verifiable image provenance from build through EKS admission.

## Implementation subtasks
- [ ] Build each service image once and tag by commit
- [ ] generate SPDX and CycloneDX SBOM with Syft
- [ ] scan with Trivy
- [ ] sign digest with Cosign keyless OIDC or KMS-backed identity
- [ ] attest SBOM to digest
- [ ] push only passing images to private ECR
- [ ] enable ECR scan-on-push
- [ ] install Kyverno or Gatekeeper policy that rejects unsigned/untrusted images and mutable tags
- [ ] retain attestations and verification evidence.

## Acceptance criteria
- [ ] A valid signed image with SBOM deploys
- [ ] unsigned, tampered, wrong-repository, or mutable-tag fixture is rejected by admission
- [ ] registry digest, signature, SBOM and commit are linked
- [ ] critical vulnerability policy blocks promotion
- [ ] no signing private key is stored as a GitHub secret

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
