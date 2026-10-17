---
id: LOC-9.16
title: "Local TLS certificates generated (e.g., via mkcert)"
category: "9. Local Kubernetes and Packaging"
status: todo
related:
  - docs/local/kubernetes/k8s-02-kind-manifests-and-workload-security-controls.md
---

# Local TLS certificates generated (e.g., via mkcert)

## What
Ingress serves TLS with locally trusted certificates.

## Current state
None.

## Subtasks
- [ ] Generate a `*.wispurl.local` cert with mkcert (or cert-manager with a CA/Vault PKI issuer)
- [ ] Store it as a TLS Secret and reference it from the Ingress
- [ ] Redirect HTTP → HTTPS

## Acceptance criteria
- [ ] The browser shows a trusted HTTPS connection to `wispurl.local`
