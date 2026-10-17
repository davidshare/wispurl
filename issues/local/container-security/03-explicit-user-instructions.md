---
id: LOC-5.03
title: "Explicit USER instructions in all Dockerfiles"
category: "5. Container Security (Local)"
status: done
related:
  - docs/local/containers/container-00-multi-stage-application-images-and-runtime-hardening.md
---

# Explicit `USER` instructions in all Dockerfiles

## What
Every Dockerfile declares `USER` explicitly rather than relying on the base image.

## Current state
All 9 app Dockerfiles end with `USER app` / `USER nextjs`; the Vault Dockerfile switches back to `USER vault`.

## Subtasks
- [x] `USER` set in every app Dockerfile
- [x] Vault Dockerfile returns to `USER vault` after installing packages

## Acceptance criteria
- [x] `grep -L '^USER' */Dockerfile` returns nothing
