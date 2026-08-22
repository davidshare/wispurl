#!/usr/bin/env bash

# Run this ONCE after your very first `docker compose up -d vault`.
# It initialises Vault, saves the unseal keys + root token to
# .vault-keys (gitignored), then unseals Vault automatically.
#
# After this script runs, you should:
#   1. Back up .vault-keys somewhere safe and offline (password manager, etc.)
#   2. Never commit .vault-keys to git
#   3. On every subsequent restart, run: make vault-unseal
#
# Usage:
#   chmod +x vault/vault-init.sh
#   ./vault/vault-init.sh

set -euo pipefail

VAULT_ADDR="${VAULT_ADDR:-https://127.0.0.1:8200}"
VAULT_CACERT="${VAULT_CACERT:-vault/tls/ca.pem}"
KEYS_FILE=".vault-keys"

export VAULT_ADDR VAULT_CACERT

echo "Waiting for Vault to be reachable"
until curl -sf --cacert "${VAULT_CACERT}" \
	"${VAULT_ADDR}/v1/sys/health?uninitok=true&sealedok=true" >/dev/null 2>&1; do
	sleep 1
done
echo "Vault is up."

# Check if already initialised
INIT_STATUS=$(curl -sf --cacert "${VAULT_CACERT}" "${VAULT_ADDR}/v1/sys/init" |
	python3 -c "import sys,json; print(json.load(sys.stdin)['initialized'])")

if [ "${INIT_STATUS}" = "True" ]; then
	echo "	Vault is already initialised."
	echo "  To unseal after a restart, run: make vault-unseal"
	exit 0
fi

echo "	 Initialising Vault..."
echo "   5 unseal key shares, threshold of 3 required to unseal."
echo "   In production: distribute these 5 keys to 5 different people."
echo ""

vault operator init \
	-key-shares=5 \
	-key-threshold=3 \
	-format=json >"${KEYS_FILE}"

chmod 600 "${KEYS_FILE}"

echo "  Vault initialised. Keys saved to ${KEYS_FILE}"
echo "  Back up .vault-keys somewhere safe (password manager, encrypted USB)."
echo "  Do NOT commit it to git. It is already in .gitignore."
echo ""

# Unseal immediately using the saved key
echo " Unsealing Vault (providing 3 of 5 keys)..."
for i in 0 1 2; do
	KEY=$(python3 -c "import json; print(json.load(open('${KEYS_FILE}'))['unseal_keys_b64'][${i}])")
	vault operator unseal "${KEY}" >/dev/null
done

ROOT_TOKEN=$(python3 -c "import json; print(json.load(open('${KEYS_FILE}'))['root_token'])")

echo " Vault is unsealed and ready."
echo ""
echo "Root token: ${ROOT_TOKEN}"
echo "Vault UI:   ${VAULT_ADDR}/ui"
echo ""
echo "Next step:"
echo "  make vault-bootstrap"