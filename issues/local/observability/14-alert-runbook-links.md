---
id: LOC-6.14
title: "Runbook links attached to alert definitions (stubs are fine for now)"
category: "6. Observability (Local Stack)"
status: done
related:
  - docs/local/observability/obs-05-local-alertmanager-rules-and-runbook-links.md
---

# Runbook links attached to alert definitions (stubs are fine for now)

## What
Every alert links to a runbook (stubs are fine initially).

## Current state
No alerts or runbooks.

## Subtasks
- [x] Create `docs/runbooks/<alert-name>.md` stubs (symptom, impact, checks, fix)
- [x] Add `runbook_url`, `summary` and `description` annotations to every rule

## Acceptance criteria
- [x] Every alert rule has a `runbook_url` that resolves to a file
