.PHONY: all setup install-gitleaks install-precommit setup-hooks scan scan-report scan-staged clean help

OS := $(shell uname -s 2>/dev/null || echo Windows)

# ─────────────────────────────────────────────
# Default target
# ─────────────────────────────────────────────
all: setup

# ─────────────────────────────────────────────
# Install gitleaks binary
# ─────────────────────────────────────────────
install-gitleaks:
	@if command -v gitleaks >/dev/null 2>&1; then \
		echo "✅ Gitleaks already installed: $$(gitleaks version 2>&1 | head -n 1)"; \
	else \
		echo "📦 Installing gitleaks..."; \
		if [ "$(OS)" = "Darwin" ]; then \
			if command -v brew >/dev/null 2>&1; then \
				brew install gitleaks; \
			else \
				echo "❌ Homebrew not found. Install it from https://brew.sh then re-run."; exit 1; \
			fi; \
		elif [ "$(OS)" = "Linux" ]; then \
			if command -v brew >/dev/null 2>&1; then \
				brew install gitleaks; \
			else \
				echo "❌ Please install gitleaks manually:"; \
				echo "   Snap:   sudo snap install gitleaks"; \
				echo "   Binary: https://github.com/gitleaks/gitleaks/releases"; \
				exit 1; \
			fi; \
		else \
			echo "❌ Windows detected. Install via:"; \
			echo "   winget install gitleaks  OR  scoop install gitleaks"; \
			exit 1; \
		fi; \
	fi

# ─────────────────────────────────────────────
# Install pre-commit framework
# ─────────────────────────────────────────────
install-precommit:
	@if command -v pre-commit >/dev/null 2>&1; then \
		echo "✅ pre-commit already installed: $$(pre-commit --version)"; \
	else \
		echo "📦 Installing pre-commit..."; \
		if command -v brew >/dev/null 2>&1; then \
			brew install pre-commit; \
		elif command -v pip3 >/dev/null 2>&1; then \
			pip3 install pre-commit; \
		elif command -v pip >/dev/null 2>&1; then \
			pip install pre-commit; \
		else \
			echo "❌ Could not install pre-commit. Install Python/pip or Homebrew first."; \
			echo "   Docs: https://pre-commit.com/#install"; \
			exit 1; \
		fi; \
	fi

# ─────────────────────────────────────────────
# Wire pre-commit hooks into this git repo
# ─────────────────────────────────────────────
setup-hooks: install-gitleaks install-precommit
	@echo "🛠  Installing pre-commit hooks into git..."
	@pre-commit install
	@echo "✅ Hooks installed. They will run automatically on every commit."

# ─────────────────────────────────────────────
# Full setup (run this once after cloning)
# ─────────────────────────────────────────────
setup: setup-hooks
	@echo ""
	@echo "🚀 Security setup complete."
	@echo "   - pre-commit hook installed (runs gitleaks on every commit)"
	@echo "   - Run 'make scan' to audit full repo history"
	@echo ""

# ─────────────────────────────────────────────
# Scan full git history for secrets (run once, before first push)
# ─────────────────────────────────────────────
scan:
	@echo "🔍 Scanning full git history for secrets..."
	@gitleaks detect --verbose
	@echo "✅ Scan complete. No secrets found."

# ─────────────────────────────────────────────
# Scan full git history and output a JSON report
# ─────────────────────────────────────────────
scan-report:
	@echo "🔍 Scanning full git history (JSON report)..."
	@gitleaks detect -f json -r gitleaks-report.json --verbose || true
	@echo "📄 Report written to gitleaks-report.json"

# ─────────────────────────────────────────────
# Scan only currently staged files (same as what the hook does)
# ─────────────────────────────────────────────
scan-staged:
	@echo "🔍 Scanning staged files..."
	@gitleaks protect --staged --verbose

# ─────────────────────────────────────────────
# Run all pre-commit hooks manually across all files
# ─────────────────────────────────────────────
run-hooks:
	@echo "🔍 Running all pre-commit hooks across all files..."
	@pre-commit run --all-files

# ─────────────────────────────────────────────
# Update pre-commit hook versions to latest
# ─────────────────────────────────────────────
update-hooks:
	@echo "⬆️  Updating pre-commit hook versions..."
	@pre-commit autoupdate
	@echo "✅ Done. Review changes to .pre-commit-config.yaml and commit them."

# ─────────────────────────────────────────────
# Tear down hooks (useful for CI or troubleshooting)
# ─────────────────────────────────────────────
clean:
	@echo "🧹 Uninstalling pre-commit hooks..."
	@pre-commit uninstall || true
	@echo "✅ Hooks removed."

# ─────────────────────────────────────────────
# Help
# ─────────────────────────────────────────────
help:
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "  setup           Install gitleaks + pre-commit + wire hooks (run this once after cloning)"
	@echo "  scan            Scan full git history for secrets"
	@echo "  scan-report     Scan full history and write gitleaks-report.json"
	@echo "  scan-staged     Scan only staged files (mirrors what the hook does)"
	@echo "  run-hooks       Run all pre-commit hooks across every file"
	@echo "  update-hooks    Bump hook versions to latest in .pre-commit-config.yaml"
	@echo "  clean           Remove pre-commit hooks from this repo"
	@echo ""