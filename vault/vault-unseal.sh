#!/usr/bin/env sh
# vault/vault-unseal.sh
#
# Runs inside the vault-unseal sidecar container on every startup.
# Handles the full Vault lifecycle:
#   - Waits for Vault to be reachable
#   - If not initialised: initialises Vault, saves keys to the mounted
#     .vault-keys path on the host, then unseals
#   - If initialised but sealed: reads keys from .vault-keys and unseals
#   - If already unsealed: exits cleanly
#
# No host dependencies. No vault CLI required. Uses the Vault HTTP API
# directly via wget. The only host requirement is make vault-certs before
# the first docker compose up.

set -eu

VAULT_ADDR="${VAULT_ADDR:-https://vault:8200}"
VAULT_CACERT="${VAULT_CACERT:-/vault/tls/ca.pem}"
KEYS_DIR="/vault/keys"
KEYS_FILE="${KEYS_DIR}/.vault-keys"

export VAULT_ADDR VAULT_CACERT

# -----------------------------------------------------------------
# Wait for Vault to be reachable
# -----------------------------------------------------------------
echo "vault-unseal: Waiting for Vault to be reachable..."
until wget -q --spider \
	--ca-certificate="${VAULT_CACERT}" \
	"${VAULT_ADDR}/v1/sys/health?uninitcode=200&sealedcode=200" 2>/dev/null; do
	sleep 2
done
echo "vault-unseal: Vault is reachable."

# -----------------------------------------------------------------
# Check initialisation status
# -----------------------------------------------------------------
INIT_RESPONSE=$(wget -qO- \
	--ca-certificate="${VAULT_CACERT}" \
	"${VAULT_ADDR}/v1/sys/init")

INITIALISED=$(echo "${INIT_RESPONSE}" |
	python3 -c "import sys, json; print(json.load(sys.stdin)['initialized'])")

# -----------------------------------------------------------------
# Initialise if needed
# -----------------------------------------------------------------
if [ "${INITIALISED}" = "False" ]; then
	echo "vault-unseal: Vault is not initialised. Initialising now..."
	echo "vault-unseal: 5 key shares, threshold of 3 required to unseal."

	mkdir -p "${KEYS_DIR}"

	INIT_RESULT=$(wget -qO- \
		--ca-certificate="${VAULT_CACERT}" \
		--post-data='{"secret_shares": 5, "secret_threshold": 3}' \
		--header="Content-Type: application/json" \
		"${VAULT_ADDR}/v1/sys/init")

	if [ -z "${INIT_RESULT}" ]; then
		echo "vault-unseal: Vault init returned empty response. Aborting."
		exit 1
	fi

	echo "${INIT_RESULT}" >"${KEYS_FILE}"
	chmod 600 "${KEYS_FILE}"

	echo "vault-unseal: Vault initialised. Keys written to ${KEYS_FILE}."
	echo "vault-unseal: Back up .vault-keys somewhere safe. Do not commit it to git."
fi

# -----------------------------------------------------------------
# Check seal status
# -----------------------------------------------------------------
SEAL_RESPONSE=$(wget -qO- \
	--ca-certificate="${VAULT_CACERT}" \
	"${VAULT_ADDR}/v1/sys/seal-status")

SEALED=$(echo "${SEAL_RESPONSE}" |
	python3 -c "import sys, json; print(json.load(sys.stdin)['sealed'])")

if [ "${SEALED}" = "False" ]; then
	echo "vault-unseal: Vault is already unsealed. Nothing to do."
	exit 0
fi

# -----------------------------------------------------------------
# Unseal using 3 of 5 keys from the keys file
# -----------------------------------------------------------------
if [ ! -f "${KEYS_FILE}" ]; then
	echo "vault-unseal: Vault is sealed but ${KEYS_FILE} not found."
	echo "vault-unseal: Cannot unseal without the keys file."
	exit 1
fi

echo "vault-unseal: Vault is sealed. Unsealing with 3 of 5 keys..."

for i in 0 1 2; do
	KEY=$(python3 -c "
import json, sys
with open('${KEYS_FILE}') as f:
    data = json.load(f)
print(data['keys_base64'][${i}])
")
	wget -qO- \
		--ca-certificate="${VAULT_CACERT}" \
		--post-data="{\"key\": \"${KEY}\"}" \
		--header="Content-Type: application/json" \
		"${VAULT_ADDR}/v1/sys/unseal" >/dev/null
	echo "vault-unseal: Key $((i + 1)) of 3 submitted."
done

# -----------------------------------------------------------------
# Verify
# -----------------------------------------------------------------
echo "vault-unseal: Verifying..."

SEALED_AFTER=$(wget -qO- \
	--ca-certificate="${VAULT_CACERT}" \
	"${VAULT_ADDR}/v1/sys/seal-status" |
	python3 -c "import sys, json; print(json.load(sys.stdin)['sealed'])")

if [ "${SEALED_AFTER}" = "False" ]; then
	echo "vault-unseal: Vault is unsealed successfully."
	echo "vault-unseal: Root token is in ${KEYS_FILE} under root_token."
else
	echo "vault-unseal: Vault is still sealed after submitting keys."
	echo "vault-unseal: Check ${KEYS_FILE} and try again."
	exit 1
fi
