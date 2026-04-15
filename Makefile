LATEST_STABLE := $(or $(shell git tag --sort=-v:refname | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$$' | head -1),v0.0.0)
CURRENT_MAJOR := $(shell echo $(LATEST_STABLE) | sed 's/^v//' | cut -d. -f1)
CURRENT_MINOR := $(shell echo $(LATEST_STABLE) | sed 's/^v//' | cut -d. -f2)
CURRENT_BUILD := $(shell echo $(LATEST_STABLE) | sed 's/^v//' | cut -d. -f3)

setup:
	@echo "Checking prerequisites..."
	@python3 --version
	@uv --version
	@echo "Installing dependencies..."
	uv sync --dev
	@echo "Installing pre-commit hooks..."
	uv run pre-commit install
	@echo "Verifying environment..."
	uv run databao --help > /dev/null
	uv run ruff check src/databao_cli > /dev/null
	uv run mypy src/databao_cli > /dev/null
	uv run pytest tests/ --co -q > /dev/null
	@echo "Environment ready."

install:
	uv tool install --force .

uninstall:
	uv tool uninstall databao

check:
	uv run pre-commit run --all-files

test:
	bash -c 'set -a; [ -f .env ] && source .env; set +a; uv run pytest tests/ -v'

test-cov:
	bash -c 'set -a; [ -f .env ] && source .env; set +a; uv run pytest tests/ -v --cov --cov-report=term-missing --cov-report=html'

test-cov-check:
	bash -c 'set -a; [ -f .env ] && source .env; set +a; uv run pytest tests/ -v --cov --cov-report=term-missing --cov-fail-under=80'

e2e-test:
	uv run --group e2e-tests pytest e2e-tests

nickname:
	@git config user.email | cut -d@ -f1

lint-skills:
	uv run python scripts/validate_agent_guidance.py

smoke-skills:
	scripts/smoke-test-skills.sh

release:
	@if [ -z "$(VERSION)" ]; then \
		echo "Usage: make release VERSION=0.3.0"; \
		exit 1; \
	fi
	@echo "Creating release v$(VERSION)..."
	git tag -a "v$(VERSION)" -m "v$(VERSION)"
	git push origin "v$(VERSION)"
	@echo "Tag v$(VERSION) pushed. CI will publish to PyPI."

patch-release: VERSION = $(CURRENT_MAJOR).$(CURRENT_MINOR).$(shell echo $$(($(CURRENT_BUILD) + 1)))
patch-release: release

minor-release: VERSION = $(CURRENT_MAJOR).$(shell echo $$(($(CURRENT_MINOR) + 1))).0
minor-release: release

major-release: VERSION = $(shell echo $$(($(CURRENT_MAJOR) + 1))).0.0
major-release: release

dev-release:
	gh workflow run publish-dev.yml
	@echo "Dev release workflow triggered."