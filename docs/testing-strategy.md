# Testing Strategy

Keep verification proportional to environment readiness.

## Modes

- `No env setup`: do not run lint/type/tests; run only smoke test.
- `Env ready`: run checks and tests with `uv`.

## No Env Setup (safe fallback)

Use this when dependencies are not installed yet or the environment is unknown.

- Smoke test: `uv run databao --help`

Goal: catch basic import/syntax breakage without full dependency resolution.

## Env Ready (normal workflow)

When `uv sync --dev` has been run and dependencies are available:

- Pre-commit: `uv run pre-commit run --all-files`
- Ruff: `uv run ruff check src/databao_cli`
- Mypy: `uv run mypy src/databao_cli`
- Unit tests: `uv run pytest tests/ -v`
- E2E tests: `uv run --group e2e-tests pytest e2e-tests`

Prefer narrow-first verification while iterating:

- Single test file: `uv run pytest tests/test_foo.py -v`
- Single test function: `uv run pytest tests/test_foo.py::test_bar -v`

## Suggested Agent Behavior

- If environment state is unclear, default to smoke test and report that
  full checks were intentionally skipped.
- If environment is ready, run the narrowest relevant test/check first,
  then broaden to full checks before finalizing larger changes.

## Make Targets

Use the `Makefile` convenience targets for common flows:

- `make check` — pre-commit (ruff + mypy)
- `make test` — unit tests (pytest)
- `make e2e-test` — end-to-end tests
