check:
	uv run pre-commit run --all-files

test:
	bash -c 'set -a; [ -f .env ] && source .env; set +a; uv run pytest tests/ -v'

e2e-test:
	uv run --group e2e-tests pytest e2e-tests