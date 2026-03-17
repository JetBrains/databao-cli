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