#!/usr/bin/env bash
# vault/generate-certs.sh
#
# Generates a self-signed CA and a Vault TLS certificate.
# Run this ONCE before `make vault-up`.
# Certs are written to vault/tls/ and are gitignored.
#
# The cert covers:
#   - vault          (Docker Compose service hostname)
#   - localhost
#   - 127.0.0.1
#
# Services that talk to Vault can either:
#   a) Set VAULT_SKIP_VERIFY=true  (quick, fine for local dev)
#   b) Mount vault/tls/ca.pem and set VAULT_CACERT=/path/to/ca.pem (more correct)

set -euo pipefail

TLS_DIR="$(dirname "$0")/tls"
mkdir -p "${TLS_DIR}"

# Skip if certs already exist
if [ -f "${TLS_DIR}/vault-cert.pem" ] && [ -f "${TLS_DIR}/vault-key.pem" ]; then
	echo "TLS certs already exist in vault/tls/. Skipping generation."
	echo "Delete vault/tls/*.pem and re-run to regenerate."
	exit 0
fi

echo "Generating self-signed CA and Vault TLS certificate..."

# 1. Generate CA key and self-signed CA cert (10 year expiry — it's local)
openssl genrsa -out "${TLS_DIR}/ca-key.pem" 4096 2>/dev/null

openssl req -new -x509 -days 3650 \
	-key "${TLS_DIR}/ca-key.pem" \
	-out "${TLS_DIR}/ca.pem" \
	-subj "/CN=vault-local-ca/O=wispurl-local" 2>/dev/null

# 2. Generate Vault server key
openssl genrsa -out "${TLS_DIR}/vault-key.pem" 4096 2>/dev/null

# 3. Generate CSR
openssl req -new \
	-key "${TLS_DIR}/vault-key.pem" \
	-out "${TLS_DIR}/vault.csr" \
	-subj "/CN=vault/O=wispurl-local" 2>/dev/null

# 4. Create SAN extension file
cat >"${TLS_DIR}/vault-ext.cnf" <<EOF
[SAN]
subjectAltName=DNS:vault,DNS:localhost,IP:127.0.0.1
EOF

# 5. Sign the cert with our CA, including SANs
openssl x509 -req -days 3650 \
	-in "${TLS_DIR}/vault.csr" \
	-CA "${TLS_DIR}/ca.pem" \
	-CAkey "${TLS_DIR}/ca-key.pem" \
	-CAcreateserial \
	-out "${TLS_DIR}/vault-cert.pem" \
	-extfile "${TLS_DIR}/vault-ext.cnf" \
	-extensions SAN 2>/dev/null

# 6. Clean up CSR and ext file (not needed after signing)
rm -f "${TLS_DIR}/vault.csr" "${TLS_DIR}/vault-ext.cnf" "${TLS_DIR}/ca.srl"

# 7. Fix permissions — Vault container runs as UID 100
chmod 644 "${TLS_DIR}/vault-cert.pem" "${TLS_DIR}/ca.pem"
chmod 600 "${TLS_DIR}/vault-key.pem" "${TLS_DIR}/ca-key.pem"

echo "Certs written to vault/tls/:"
echo "   vault/tls/ca.pem         CA cert (share with services that need to verify Vault)"
echo "   vault/tls/vault-cert.pem Vault server cert"
echo "   vault/tls/vault-key.pem  Vault server private key (keep private)"
echo "   vault/tls/ca-key.pem     CA private key (keep private, only needed to re-sign)"
echo ""
echo "Services can skip TLS verification with VAULT_SKIP_VERIFY=true"
echo "or verify properly by mounting ca.pem and setting VAULT_CACERT=/path/to/ca.pem"
