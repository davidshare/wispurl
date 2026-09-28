---
id: local-002
title: Multi-stage application images and runtime hardening
type: feat
feature: 1. Application Foundations
status: not_started
depends_on: []
checklist_sections: 1. Application Foundations; 5. Container Security
---

# Multi-stage application images and runtime hardening

## Goal
Harden build and runtime images for every application and Vault image without changing each service’s documented runtime contract. Targets: auth, shortener, analytics API, analytics consumer, cleanup, notification, rate limiter, QR, gateway, frontend, and Vault.

## Implementation subtasks
- [x] Use separate build and runtime stages for application Dockerfiles; keep the Vault image based on the upstream Vault image because it does not compile an application
- [ ] pin base image versions or digests
- [x] run as a dedicated non-root UID in every application and Vault runtime image
- [ ] ensure final stages contain no compilers, package managers, source credentials, or build secrets unless required
- [ ] set writable paths explicitly
- [ ] document each service’s required writable directories
- [ ] run compatible containers with read-only root filesystems and dropped capabilities in Compose
- [ ] define CPU and memory limits for every Compose service
- [ ] use image scanning evidence to select minimal supported bases.

## Acceptance criteria
- [ ] Every listed Dockerfile builds
- [ ] each final image runs as non-root
- [ ] no image uses latest
- [ ] image inspection finds no credentials or build-only toolchain
- [ ] application services start with read-only root filesystem where compatible and document any exception
- [ ] Compose declares bounded CPU/memory and dropped capabilities
- [ ] exceptions name the service and writable path

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
