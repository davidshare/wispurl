---
id: LOC-5.02
title: "Containers run as non-root user"
category: "5. Container Security (Local)"
status: done
related:
  - docs/local/containers/container-00-multi-stage-application-images-and-runtime-hardening.md
---

# Containers run as non-root user

## What
Application containers run as an unprivileged user.

## Current state
Python images create a system `app` user, the frontend runs as `nextjs`, and Vault runs as `vault`.

## Subtasks
- [x] Dedicated non-root user created in each runtime image
- [x] Files copied with `--chown` to that user

## Acceptance criteria
- [x] `docker compose exec <svc> id -u` is not 0 for every app service

## References
- [auth-service/Dockerfile](../../../auth-service/Dockerfile)
