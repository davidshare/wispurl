.PHONY: all setup install-gitleaks install-precommit setup-hooks scan scan-report \
        scan-staged run-hooks update-hooks clean help \
        vault-certs vault-up vault-unseal vault-bootstrap \
        vault-status vault-env vault-snapshot vault-down vault-clean

OS := $(shell uname -s 2>/dev/null || echo Windows)

all: setup

# -----------------------------------------------------------------
# SECRETS SCANNING
# -----------------------------------------------------------------

install-gitleaks:
	@if command -v gitleaks >/dev/null 2>&1; then \
		echo "Gitleaks already installed: $$(gitleaks version 2>&1 | head -n 1)"; \
	else \
		echo "Installing gitleaks..."; \
		if [ "$(OS)" = "Darwin" ]; then \
			if command -v brew >/dev/null 2>&1; then \
				brew install gitleaks; \
			else \
				echo "Homebrew not found. Install it from https://brew.sh then re-run."; exit 1; \
			fi; \
		elif [ "$(OS)" = "Linux" ]; then \
			if command -v brew >/dev/null 2>&1; then \
				brew install gitleaks; \
			else \
				echo "Please install gitleaks manually:"; \
				echo "   Snap:   sudo snap install gitleaks"; \
				echo "   Binary: https://github.com/gitleaks/gitleaks/releases"; \
				exit 1; \
			fi; \
		else \
			echo "Windows detected. Install via:"; \
			echo "   winget install gitleaks  OR  scoop install gitleaks"; \
			exit 1; \
		fi; \
	fi

# -----------------------------------------------------------------
# Install pre-commit framework
# -----------------------------------------------------------------
install-precommit:
	@if command -v pre-commit >/dev/null 2>&1; then \
		echo "pre-commit already installed: $$(pre-commit --version)"; \
	else \
		echo "Installing pre-commit..."; \
		if command -v brew >/dev/null 2>&1; then \
			brew install pre-commit; \
		elif command -v pip3 >/dev/null 2>&1; then \
			pip3 install pre-commit; \
		elif command -v pip >/dev/null 2>&1; then \
			pip install pre-commit; \
		else \
			echo "Could not install pre-commit. Install Python/pip or Homebrew first."; \
			echo "   Docs: https://pre-commit.com/#install"; \
			exit 1; \
		fi; \
	fi

# -----------------------------------------------------------------
# Wire pre-commit hooks into this git repo
# -----------------------------------------------------------------
setup-hooks: install-gitleaks install-precommit
	@echo "Installing pre-commit hooks into git..."
	@pre-commit install
	@echo "Hooks installed. They will run automatically on every commit."

# -----------------------------------------------------------------
# Full setup (run this once after cloning)
# -----------------------------------------------------------------
setup: setup-hooks
	@echo ""
	@echo "Security setup complete."
	@echo "   - pre-commit hook installed (runs gitleaks on every commit)"
	@echo "   - Run 'make scan' to audit full repo history"
	@echo ""

# -----------------------------------------------------------------
# Scan full git history for secrets (run once, before first push)
# -----------------------------------------------------------------
scan:
	@echo "Scanning full git history for secrets..."
	@gitleaks detect --verbose
	@echo "Scan complete. No secrets found."

# -----------------------------------------------------------------
# Scan full git history and output a JSON report
# -----------------------------------------------------------------
scan-report:
	@echo "Scanning full git history (JSON report)..."
	@gitleaks detect -f json -r gitleaks-report.json --verbose || true
	@echo "Report written to gitleaks-report.json"

# -----------------------------------------------------------------
# Scan only currently staged files (same as what the hook does)
# -----------------------------------------------------------------
scan-staged:
	@echo "Scanning staged files..."
	@gitleaks protect --staged --verbose

# -----------------------------------------------------------------
# Run all pre-commit hooks manually across all files
# -----------------------------------------------------------------
run-hooks:
	@echo "Running all pre-commit hooks across all files..."
	@pre-commit run --all-files

# -----------------------------------------------------------------
# Update pre-commit hook versions to latest
# -----------------------------------------------------------------
update-hooks:
	@echo "Updating pre-commit hook versions..."
	@pre-commit autoupdate
	@echo "Done. Review changes to .pre-commit-config.yaml and commit them."

# -----------------------------------------------------------------
# Tear down hooks (useful for CI or troubleshooting)
# -----------------------------------------------------------------
clean:
	@echo "Uninstalling pre-commit hooks..."
	@pre-commit uninstall || true
	@echo "Hooks removed."


# -----------------------------------------------------------------
# VAULT
# -----------------------------------------------------------------

# Generate self-signed TLS certs.
# Skips automatically if certs already exist.
vault-certs:
	@chmod +x vault/generate-certs.sh
	@./vault/generate-certs.sh

# Start Vault and the unseal sidecar.
# Generates TLS certs first if they do not exist.
# The unseal sidecar handles init and unseal automatically.
# No vault CLI required on the host.
vault-up: vault-certs
	@echo "Starting Vault..."
	@docker compose up -d vault vault-unseal
	@echo "Vault container started."
	@echo "The unseal sidecar will initialise and unseal Vault automatically."
	@echo "Watch progress with: docker logs -f vault-unseal"
	@echo "Once vault-unseal exits cleanly, run: make vault-bootstrap"

# Restart the unseal sidecar.
# Use this if Vault restarted and is sealed again.
vault-unseal:
	@echo "Restarting vault-unseal sidecar..."
	@docker compose restart vault-unseal
	@echo "Watch progress with: docker logs -f vault-unseal"

# Bootstrap: enable KV, audit logging, create AppRoles for all services.
# Run once after vault-unseal exits cleanly on first boot.
vault-bootstrap:
	@echo "Bootstrapping Vault..."
	@mkdir -p vault/approles
	@if [ -f vault/keys/.vault-keys ]; then \
		KEYS="vault/keys/.vault-keys"; \
	elif [ -f .vault-keys ]; then \
		KEYS=".vault-keys"; \
	else \
		echo "Keys file not found in vault/keys/.vault-keys or .vault-keys. Has vault-unseal completed successfully?"; exit 1; \
	fi; \
	TOKEN=$$(python3 -c "import json; print(json.load(open('$$KEYS'))['root_token'])"); \
	docker cp vault/vault-bootstrap.sh vault:/vault/vault-bootstrap.sh; \
	if [ -f .env ]; then \
		docker cp .env vault:/vault/.env; \
	fi; \
	docker exec \
		-e VAULT_ADDR=https://127.0.0.1:8200 \
		-e VAULT_CACERT=/vault/tls/ca.pem \
		-e VAULT_TOKEN="$$TOKEN" \
		vault sh /vault/vault-bootstrap.sh; \
	docker exec vault rm -f /vault/.env /vault/vault-bootstrap.sh

# Check Vault sealed/unsealed status.
# Runs inside the vault container — no vault CLI needed on the host.
vault-status:
	@docker exec vault sh -c \
		"VAULT_CACERT=/vault/tls/ca.pem vault status -address=https://127.0.0.1:8200" || true

# Pull secrets for a service and write them to <service>/.env
# Usage: make vault-env SERVICE=auth-service
vault-env:
	@if [ -z "$(SERVICE)" ]; then \
		echo "Specify a service: make vault-env SERVICE=auth-service"; exit 1; \
	fi
	@if [ -f vault/keys/.vault-keys ]; then \
		KEYS="vault/keys/.vault-keys"; \
	elif [ -f .vault-keys ]; then \
		KEYS=".vault-keys"; \
	else \
		echo "Keys file not found in vault/keys/.vault-keys or .vault-keys. Has vault-unseal completed successfully?"; exit 1; \
	fi; \
	echo "Writing $(SERVICE)/.env from Vault..."; \
	ROOT_TOKEN=$$(python3 -c "import json; print(json.load(open('$$KEYS'))['root_token'])"); \
	docker exec \
		-e VAULT_TOKEN="$$ROOT_TOKEN" \
		-e VAULT_CACERT=/vault/tls/ca.pem \
		vault \
		vault kv get -format=json \
		-address=https://127.0.0.1:8200 \
		"secret/wispurl/$(SERVICE)" \
	| python3 -c " \
import json, sys; \
d = json.load(sys.stdin)['data']['data']; \
print('\n'.join(f'{k}={v}' for k,v in d.items())) \
" > "$(SERVICE)/.env"
	@echo "Written to $(SERVICE)/.env"
	@echo "Remember: .env files are gitignored. Re-run this after any secret rotation."

# Take a Raft snapshot backup.
# Snapshot is saved inside the container at /vault/snapshots/ (mapped to host).
vault-snapshot:
	@echo "Taking Raft snapshot..."
	@mkdir -p vault/snapshots
	@if [ -f vault/keys/.vault-keys ]; then \
		KEYS="vault/keys/.vault-keys"; \
	elif [ -f .vault-keys ]; then \
		KEYS=".vault-keys"; \
	else \
		echo "Keys file not found in vault/keys/.vault-keys or .vault-keys. Has vault-unseal completed successfully?"; exit 1; \
	fi; \
	ROOT_TOKEN=$$(python3 -c "import json; print(json.load(open('$$KEYS'))['root_token'])"); \
	docker exec \
		-e VAULT_TOKEN="$$ROOT_TOKEN" \
		-e VAULT_CACERT=/vault/tls/ca.pem \
		vault \
		vault operator raft snapshot save \
		-address=https://127.0.0.1:8200 \
		/vault/snapshots/vault-$$(date +%Y%m%d_%H%M%S).snap
	@echo "Snapshot saved to vault/snapshots/"

# Stop Vault and the unseal sidecar.
# Data persists in vault/data/.
vault-down:
	@echo "Stopping Vault..."
	@docker compose stop vault vault-unseal
	@echo "Vault stopped. Data persisted in vault/data/."

# Reset Vault state (data, keys, logs, snapshots, approles) for a clean restart.
vault-clean: vault-down
	@rm -rf vault/data/* vault/logs/* vault/keys/* vault/snapshots/* vault/approles/*.json .vault-keys
	@echo "Vault data, keys, logs, and approles cleaned."


# -----------------------------------------------------------------
# HELP
# -----------------------------------------------------------------

help:
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "Secrets scanning:"
	@echo "  setup           Install gitleaks + pre-commit + wire hooks (run this once after cloning)"
	@echo "  scan            Scan full git history for secrets"
	@echo "  scan-report     Scan full history and write gitleaks-report.json"
	@echo "  scan-staged     Scan only staged files (mirrors what the hook does)"
	@echo "  run-hooks       Run all pre-commit hooks across every file"
	@echo "  update-hooks    Bump hook versions in .pre-commit-config.yaml"
	@echo "  clean           Remove pre-commit hooks from this repo"
	@echo ""
	@echo "Vault:"
	@echo "  vault-up        Generate TLS certs if needed, start Vault and unseal sidecar"
	@echo "  vault-unseal    Restart the unseal sidecar (use after Vault restarts)"
	@echo "  vault-bootstrap Enable KV, audit log, create AppRoles for all services"
	@echo "  vault-status    Check Vault sealed/unsealed status"
	@echo "  vault-env       Write service secrets to .env file"
	@echo "                  Usage: make vault-env SERVICE=auth-service"
	@echo "  vault-snapshot  Take a Raft snapshot backup"
	@echo "  vault-down      Stop Vault and unseal sidecar"
	@echo "  vault-clean     Reset all Vault data, keys, logs, and approles"
	@echo ""
	@echo "First-time order:"
	@echo "  make setup"
	@echo "  make vault-up"
	@echo "  (wait for vault-unseal to exit cleanly: docker logs -f vault-unseal)"
	@echo "  make vault-bootstrap"
	@echo "  make scan"
	@echo ""