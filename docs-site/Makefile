# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   🐍 IBMCloud README Static Docs Site - Makefile
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# Author: Maxim Shelepov
# Description: Builds/serves for production viewing or development.
# Usage: run `make docs`, `make docs-dev`, or `make help` to view available targets.
#
# help: 🛠️ IBMCloud Docs Site
#
# ──────────────────────────────────────────────────────────────────────────
# Project variables
PROJECT_NAME      = ibm-cloud-docs
# =============================================================================
# 📖 DYNAMIC HELP
# =============================================================================
.PHONY: help
help:
	@grep "^# help\:" Makefile | grep -v grep | sed 's/\# help\: //' | sed 's/\# help\://'

.PHONY: docs

docs:
	bash scripts/build-serve.sh
docs-dev:
	bash scripts/dev-run.sh
