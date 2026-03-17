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