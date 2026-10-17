---
id: LOC-10.03
title: "TLS used locally wherever practical"
category: "10. Security and Compliance (Local)"
status: partial
---

# TLS used locally wherever practical

## What
TLS is used locally wherever practical.

## Current state
Vault serves TLS from a local CA and services verify it. Everything else is plaintext, and the frontend, gateway and debug APIs listen on all host interfaces.

## Subtasks
- [x] Vault TLS with local CA, verified by clients
- [ ] Ingress TLS (see Kubernetes local TLS)
- [ ] Postgres TLS (`ssl=on`, clients `sslmode=verify-full`) where practical
- [ ] RabbitMQ TLS (optional)
- [ ] Bind frontend/gateway/debug ports to `127.0.0.1`
- [ ] Document what stays plaintext and why

## Acceptance criteria
- [ ] Every plaintext link is either encrypted or listed with a justification
