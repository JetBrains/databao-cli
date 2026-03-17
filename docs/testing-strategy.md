# Testing Strategy

Always run checks and tests locally before pushing code.

## Quick Start

```bash
uv sync --dev                        # install/update deps (once)
make check                           # lint + type-check (ruff + mypy)
make test                            # unit tests
uv run databao --help                # smoke-test the CLI entrypoint
```

## Verification Workflow

Follow this order when making changes:

1. **Lint & format** — `uv run ruff check src/databao_cli` and
   `uv run ruff format --check src/databao_cli`. Fast; catches syntax,
   import, and style issues immediately.
2. **Type-check** — `uv run mypy src/databao_cli`. Strict mode is enabled;
   fix all errors before proceeding.
3. **Unit tests** — `uv run pytest tests/ -v`. Covers commands, MCP tools,
   query execution, and datasource checks.
4. **Smoke test** — `uv run databao --help`. Confirms the CLI entrypoint
   loads without import errors.
5. **E2E tests** — `make e2e-test` (requires Docker / external services).
   Run when changing datasource integrations or the build pipeline.

## Narrowing Scope While Iterating

Run the smallest relevant slice first, then broaden before finalizing:

- Single test file: `uv run pytest tests/test_init.py -v`
- Single test function: `uv run pytest tests/test_init.py::test_bar -v`
- Single ruff rule: `uv run ruff check src/databao_cli --select TID252`
- Changed files only: `uv run pre-commit run --files src/databao_cli/commands/init.py`

## Unit Tests (`tests/`)

- Use `pytest` with the `project_layout` fixture from `conftest.py` for
  tests that need an initialized project directory.
- Keep tests focused: one behavior per test function.
- Add a regression test for every bug fix when feasible.
- Test files mirror source modules (e.g., `test_init.py` tests `commands/init.py`).

## E2E Tests (`e2e-tests/`)

- Use `pexpect`, `testcontainers`, and `allure-pytest`.
- Domain-specific tests live under `e2e-tests/tests/domains/` (SQLite, Postgres,
  DuckDB, MySQL, BigQuery, Snowflake).
- Introspection fixtures live under `e2e-tests/tests/resources/`.
- Run with: `uv run --group e2e-tests pytest e2e-tests`.
- These require Docker and sometimes cloud credentials — not expected to pass
  on every local machine, but always run in CI.

## Make Targets

| Target         | Command                                              | What it does               |
|----------------|------------------------------------------------------|----------------------------|
| `make check`        | `uv run pre-commit run --all-files`                  | Ruff lint + mypy                  |
| `make test`         | `uv run pytest tests/ -v` (sources `.env` if present)| Unit tests                        |
| `make test-cov`     | `uv run pytest ... --cov`                            | Coverage report (no threshold)    |
| `make test-cov-check`| `uv run pytest ... --cov --cov-fail-under=80`       | Coverage with 80% enforcement     |
| `make e2e-test`     | `uv run --group e2e-tests pytest e2e-tests`          | End-to-end tests (Docker)         |

## Coverage

Unit test coverage is measured with `pytest-cov` and enforced at **80%**.

Configuration lives in `pyproject.toml` under `[tool.coverage.*]` sections.

**What to cover**: CLI commands, MCP tools, query execution, datasource checks,
project management, and utility functions.

**What is excluded**: Streamlit UI (`src/databao_cli/ui/`) is tested via e2e
tests, not unit coverage. The `__main__.py` entrypoint wrapper is also excluded.

**When coverage drops**: See the `check-coverage` skill for the decision
procedure on whether to fix code or fix tests.

## Agent Behavior

Agents should **always** run verification locally:

- After any code change, run at minimum `make check` and the relevant unit
  tests before considering the change complete.
- Run `uv run databao --help` after modifying CLI entrypoints, commands, or
  top-level imports.
- If a test fails, diagnose and fix — do not skip or ignore failures.
- If the environment is not set up, run `uv sync --dev` to set it up rather
  than falling back to a smoke-test-only mode.
- Run full `make test` before finalizing larger changes that touch multiple
  modules.
- After code changes, run `make test-cov-check` to verify coverage ≥80%.
