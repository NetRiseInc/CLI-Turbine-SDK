# GitHub sync configuration
GITHUB_CLI_REPO = git@github.com:NetRiseInc/CLI-Turbine-SDK.git
GITHUB_SYNC_TMP = .tmp/cli-github-sync
CLI_VERSION := $(shell grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
GITHUB_SYNC_BRANCH_STAMP := $(shell date +%Y-%m-%d-%H%M)
BRANCH ?= sync/$(CLI_VERSION)-$(GITHUB_SYNC_BRANCH_STAMP)

.PHONY: venv install install-dev test test-v clean github-sync

venv:
	python3 -m venv .venv

install: venv
	.venv/bin/pip install -e .

install-dev: venv
	.venv/bin/pip install -e ".[dev]"

test: install-dev
	.venv/bin/pytest tests/

test-v: install-dev
	.venv/bin/pytest tests/ -v

clean:
	rm -rf .venv build dist *.egg-info src/*.egg-info .pytest_cache .tmp
	find . -type d -name __pycache__ -exec rm -rf {} +

github-sync: ## Sync CLI to GitHub (branch: sync/<version>-<timestamp>); override with BRANCH=
	@echo "→ Sync branch: $(BRANCH)"
	@echo "→ Preparing temp directory..."
	@rm -rf "$(GITHUB_SYNC_TMP)"
	@mkdir -p "$(GITHUB_SYNC_TMP)"
	@echo "→ Cloning GitHub repo..."
	@git clone "$(GITHUB_CLI_REPO)" "$(GITHUB_SYNC_TMP)" 2>&1 | grep -v "Cloning into" || true
	@cd "$(GITHUB_SYNC_TMP)" && git checkout -b "$(BRANCH)" 2>/dev/null || git checkout "$(BRANCH)"
	@echo "→ Syncing CLI to GitHub repo..."
	@rsync -a --delete \
		--exclude='.venv/' \
		--exclude='__pycache__/' \
		--exclude='*.pyc' \
		--exclude='dist/' \
		--exclude='.env' \
		--exclude='.pytest_cache/' \
		--exclude='.git/' \
		--exclude='.tmp/' \
		./ "$(GITHUB_SYNC_TMP)/"
	@cd "$(GITHUB_SYNC_TMP)" && git add -A && \
		if git diff --cached --quiet; then \
			echo "✓ No changes to commit"; \
		else \
			git commit -m "Sync CLI from monorepo" && \
			echo "✓ Changes committed"; \
		fi
	@echo "→ Pushing to origin/$(BRANCH)..."
	@cd "$(GITHUB_SYNC_TMP)" && git push -u origin "$(BRANCH)"
	@echo "✓ Synced to GitHub: $(GITHUB_CLI_REPO) (branch: $(BRANCH))"
	@rm -rf "$(GITHUB_SYNC_TMP)"
	@echo "→ Open PR: https://github.com/NetRiseInc/CLI-Turbine-SDK/compare/$(BRANCH)"
