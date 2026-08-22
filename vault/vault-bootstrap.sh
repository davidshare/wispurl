#!/usr/bin/env bash

# Run ONCE after vault-unseal exits cleanly on first boot.
# - Enables KV v2 secrets engine
# - Enables audit logging to /vault/logs/audit.log
# - Creates a scoped policy + AppRole for every wispurl service
# - Writes secret skeletons matching microservice configuration schemas
#
# Saves each service's role_id and secret_id to vault/approles/<service>.json
# Those files are gitignored. Your services use them to authenticate with Vault.
#
# Usage (called automatically via: make vault-bootstrap):
#   make vault-bootstrap

set -euo pipefail

VAULT_ADDR="${VAULT_ADDR:-https://127.0.0.1:8200}"
VAULT_CACERT="${VAULT_CACERT:-vault/tls/ca.pem}"
APPROLES_DIR="${APPROLES_DIR:-vault/approles}"

export VAULT_ADDR VAULT_CACERT

if [ -z "${VAULT_TOKEN:-}" ]; then
	if [ -f "vault/keys/.vault-keys" ]; then
		KEYS_FILE="vault/keys/.vault-keys"
	elif [ -f "/vault/keys/.vault-keys" ]; then
		KEYS_FILE="/vault/keys/.vault-keys"
	elif [ -f ".vault-keys" ]; then
		KEYS_FILE=".vault-keys"
	else
		echo "Keys file not found (.vault-keys or vault/keys/.vault-keys). Has vault-unseal completed successfully?"
		exit 1
	fi
	VAULT_TOKEN=$(python3 -c "import json; print(json.load(open('${KEYS_FILE}'))['root_token'])" 2>/dev/null || true)
	if [ -z "${VAULT_TOKEN}" ]; then
		echo "Could not parse root_token from ${KEYS_FILE}. Please pass VAULT_TOKEN in environment."
		exit 1
	fi
fi

export VAULT_TOKEN

mkdir -p "${APPROLES_DIR}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Vault Bootstrap — wispurl"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# --- 1. Enable audit logging
echo "Enabling audit logging..."
vault audit enable file file_path=/vault/logs/audit.log 2>/dev/null &&
	echo "   Audit log: /vault/logs/audit.log" ||
	echo "   Audit logging already enabled."

# --- 2. Enable KV v2
echo ""
echo "Enabling KV v2 secrets engine..."
vault secrets enable -path=secret kv-v2 2>/dev/null &&
	echo "   KV v2 enabled at secret/" ||
	echo "   KV v2 already enabled."

# --- 3. Enable AppRole auth
echo ""
echo "Enabling AppRole auth method..."
vault auth enable approle 2>/dev/null &&
	echo "   AppRole enabled." ||
	echo "   AppRole already enabled."

# --- 4. Write secret skeletons and create AppRole per service
echo ""
echo "Writing secrets and creating AppRoles for each service..."
echo ""

# Load environment variables if an env file is provided or exists
if [ -n "${ENV_FILE:-}" ] && [ -f "${ENV_FILE}" ]; then
	echo "Loading seed configuration from ${ENV_FILE}..."
	set -a
	# shellcheck disable=SC1090
	. "${ENV_FILE}"
	set +a
elif [ -f "/vault/.env" ]; then
	echo "Loading seed configuration from /vault/.env..."
	set -a
	. "/vault/.env"
	set +a
elif [ -f ".env" ]; then
	echo "Loading seed configuration from .env..."
	set -a
	. ".env"
	set +a
fi

SERVICES=(
	"auth-service"
	"analytics-service"
	"shortener-service"
	"gateway"
	"cleanup-service"
	"notification-service"
	"qr-service"
	"rate-limiter-service"
)

for SERVICE in "${SERVICES[@]}"; do
	echo "  -- ${SERVICE}"

	case "${SERVICE}" in
	auth-service)
		vault kv put "secret/wispurl/${SERVICE}" \
			DATABASE_URL="${AUTH_DATABASE_URL:-postgresql+psycopg://user:your-db-password-here@postgres:5432/auth_db}" \
			JWT_SECRET="${JWT_SECRET:-your-jwt-secret-key-here}" \
			JWT_ALGORITHM="${JWT_ALGORITHM:-HS256}" \
			ACCESS_TOKEN_TTL_MINUTES="${ACCESS_TOKEN_TTL_MINUTES:-15}" \
			REFRESH_TOKEN_TTL_DAYS="${REFRESH_TOKEN_TTL_DAYS:-7}" \
			CORS_ALLOWED_ORIGINS="${CORS_ALLOWED_ORIGINS:-http://localhost:3000}" \
			LOG_LEVEL="${LOG_LEVEL:-INFO}" >/dev/null
		;;
	analytics-service)
		vault kv put "secret/wispurl/${SERVICE}" \
			DATABASE_URL="${ANALYTICS_DATABASE_URL:-postgresql+psycopg://user:your-db-password-here@postgres:5432/stats_db}" \
			INTERNAL_API_KEY="${INTERNAL_API_KEY:-your-internal-api-key-here}" \
			JWT_SECRET="${JWT_SECRET:-your-jwt-secret-key-here}" \
			JWT_ALGORITHM="${JWT_ALGORITHM:-HS256}" \
			MILESTONES="${MILESTONES:-100,1000,10000}" \
			RABBITMQ_URL="${RABBITMQ_URL:-amqp://user:your-rabbitmq-password-here@rabbitmq:5672/}" \
			CORS_ALLOWED_ORIGINS="${CORS_ALLOWED_ORIGINS:-http://localhost:3000}" \
			LOG_LEVEL="${LOG_LEVEL:-INFO}" >/dev/null
		;;
	shortener-service)
		vault kv put "secret/wispurl/${SERVICE}" \
			DATABASE_URL="${SHORTENER_DATABASE_URL:-postgresql+psycopg://user:your-db-password-here@postgres:5432/short_db}" \
			INTERNAL_API_KEY="${INTERNAL_API_KEY:-your-internal-api-key-here}" \
			JWT_SECRET="${JWT_SECRET:-your-jwt-secret-key-here}" \
			JWT_ALGORITHM="${JWT_ALGORITHM:-HS256}" \
			PUBLIC_BASE_URL="${PUBLIC_BASE_URL:-http://localhost:8002}" \
			RATE_LIMITER_URL="${RATE_LIMITER_URL:-http://rate-limiter-service:8000}" \
			ANALYTICS_SERVICE_URL="${ANALYTICS_SERVICE_URL:-http://analytics-service:8000}" \
			RABBITMQ_URL="${RABBITMQ_URL:-amqp://user:your-rabbitmq-password-here@rabbitmq:5672/}" \
			LOG_LEVEL="${LOG_LEVEL:-INFO}" >/dev/null
		;;
	gateway)
		vault kv put "secret/wispurl/${SERVICE}" \
			JWT_SECRET="${JWT_SECRET:-your-jwt-secret-key-here}" \
			JWT_ALGORITHM="${JWT_ALGORITHM:-HS256}" \
			AUTH_SERVICE_URL="${AUTH_SERVICE_URL:-http://auth-service:8000}" \
			SHORTENER_SERVICE_URL="${SHORTENER_SERVICE_URL:-http://shortener-service:8000}" \
			ANALYTICS_SERVICE_URL="${ANALYTICS_SERVICE_URL:-http://analytics-service:8000}" \
			QR_SERVICE_URL="${QR_SERVICE_URL:-http://qr-service:8000}" \
			CORS_ALLOWED_ORIGINS="${CORS_ALLOWED_ORIGINS:-http://localhost:3000}" \
			LOG_LEVEL="${LOG_LEVEL:-INFO}" >/dev/null
		;;
	cleanup-service)
		vault kv put "secret/wispurl/${SERVICE}" \
			DATABASE_URL="${SHORTENER_DATABASE_URL:-postgresql+psycopg://user:your-db-password-here@postgres:5432/short_db}" \
			RABBITMQ_URL="${RABBITMQ_URL:-amqp://user:your-rabbitmq-password-here@rabbitmq:5672/}" \
			CLEANUP_INTERVAL_SECONDS="${CLEANUP_INTERVAL_SECONDS:-60}" \
			BATCH_SIZE="${BATCH_SIZE:-500}" \
			LOG_LEVEL="${LOG_LEVEL:-INFO}" >/dev/null
		;;
	notification-service)
		vault kv put "secret/wispurl/${SERVICE}" \
			RABBITMQ_URL="${RABBITMQ_URL:-amqp://user:your-rabbitmq-password-here@rabbitmq:5672/}" \
			NOTIFY_CHANNEL="${NOTIFY_CHANNEL:-log}" \
			SMTP_HOST="${SMTP_HOST:-smtp.example.com}" \
			SMTP_PORT="${SMTP_PORT:-587}" \
			SMTP_USERNAME="${SMTP_USERNAME:-your-smtp-username-here}" \
			SMTP_PASSWORD="${SMTP_PASSWORD:-your-smtp-password-here}" \
			LOG_LEVEL="${LOG_LEVEL:-INFO}" >/dev/null
		;;
	qr-service)
		vault kv put "secret/wispurl/${SERVICE}" \
			JWT_SECRET="${JWT_SECRET:-your-jwt-secret-key-here}" \
			JWT_ALGORITHM="${JWT_ALGORITHM:-HS256}" \
			PUBLIC_BASE_URL="${PUBLIC_BASE_URL:-http://localhost:8080}" \
			MIN_SIZE_PX="${MIN_SIZE_PX:-64}" \
			MAX_SIZE_PX="${MAX_SIZE_PX:-1024}" \
			DEFAULT_SIZE_PX="${DEFAULT_SIZE_PX:-256}" \
			CACHE_TTL="${CACHE_TTL:-86400}" \
			LOG_LEVEL="${LOG_LEVEL:-INFO}" >/dev/null
		;;
	rate-limiter-service)
		vault kv put "secret/wispurl/${SERVICE}" \
			REDIS_URL="${REDIS_URL:-redis://redis:6379/0}" \
			INTERNAL_API_KEY="${INTERNAL_API_KEY:-your-internal-api-key-here}" \
			JWT_SECRET="${JWT_SECRET:-your-jwt-secret-key-here}" \
			JWT_ALGORITHM="${JWT_ALGORITHM:-HS256}" \
			WINDOW_SECONDS="${WINDOW_SECONDS:-3600}" \
			CREATE_LINK_LIMIT="${CREATE_LINK_LIMIT:-20}" \
			LOG_LEVEL="${LOG_LEVEL:-INFO}" >/dev/null
		;;
	esac
	echo "     secret written"

	vault policy write "${SERVICE}" - <<EOF
# ${SERVICE} — read-only access to its own secrets only
path "secret/data/wispurl/${SERVICE}" {
    capabilities = ["read"]
}
path "secret/metadata/wispurl/${SERVICE}" {
    capabilities = ["read"]
}
path "auth/token/renew-self" {
    capabilities = ["update"]
}
EOF
	echo "     policy written"

	vault write "auth/approle/role/${SERVICE}" \
		token_policies="${SERVICE}" \
		token_ttl="1h" \
		token_max_ttl="4h" \
		secret_id_ttl="0" \
		secret_id_num_uses="0" >/dev/null

	ROLE_ID=$(vault read -field=role_id "auth/approle/role/${SERVICE}/role-id")
	SECRET_ID=$(vault write -field=secret_id -f "auth/approle/role/${SERVICE}/secret-id")

	cat >"${APPROLES_DIR}/${SERVICE}.json" <<EOF
{
  "role_id": "${ROLE_ID}",
  "secret_id": "${SECRET_ID}",
  "service": "${SERVICE}"
}
EOF
	chmod 600 "${APPROLES_DIR}/${SERVICE}.json"
	echo "     AppRole saved to ${APPROLES_DIR}/${SERVICE}.json"
	echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Bootstrap complete."
echo ""
echo "Next steps:"
echo "  1. Replace placeholder values for each service:"
echo "     vault kv patch secret/wispurl/auth-service JWT_SECRET=..."
echo "     or use the UI at ${VAULT_ADDR}/ui"
echo ""
echo "  2. Pull secrets into a service .env file:"
echo "     make vault-env SERVICE=auth-service"
echo ""
echo "  3. Each service's AppRole credentials are in vault/approles/<service>.json"
echo "     These are gitignored. Services use them to authenticate with Vault."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
