---
id: LOC-7.01
title: "Timeouts configured on every external network call"
category: "7. Reliability and SRE (Local Validation)"
status: partial
related:
  - docs/local/app/app-04-resilience-controls-for-outbound-calls-and-message-processing.md
---

# Timeouts configured on every external network call

## What
Every network call has an explicit, bounded timeout, and the timeouts nest correctly (callers wait longer than callees).

## Current state
Timeouts exist for gateway httpx (connect/read), shortener → analytics/rate-limiter, Redis sockets and Postgres server-side. `hvac.Client`, aio-pika connections and SMTP have none.

## Subtasks
- [x] Gateway httpx connect/read timeouts
- [x] Shortener analytics and rate-limiter request timeouts
- [x] Redis socket and connect timeouts
- [x] Postgres `statement_timeout` and `idle_in_transaction_session_timeout`
- [ ] Add `timeout=` to `hvac.Client` in `vault_client`
- [ ] Add aio-pika connect and publish timeouts
- [ ] Set SQLAlchemy `pool_timeout` and libpq `connect_timeout`
- [ ] Add a timeout to notification SMTP and to frontend server-side fetches to the gateway
- [ ] Document the timeout budget per hop

## Acceptance criteria
- [ ] Every outbound client in the codebase has an explicit timeout (verified by grep/review)
