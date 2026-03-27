# Testing Strategy

Always run checks and tests locally before pushing code.

## Quick Start

```bash
make setup                           # install deps, hooks, verify toolchain (once)
make check                           # lint + type-check (ruff + mypy)
make test                            # unit tests
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

## What Does NOT Run in CI / Pre-commit

Everything above (lint, type-check, unit tests, skill validation) is
**LLM-free** and runs automatically in CI and pre-commit hooks.

The following require LLM access and are **manual or agentic only**:

- **Tier 3 skill evals** (`eval-skills` skill) — agent-in-the-loop evaluation
- **E2E tests** (`make e2e-test`) — require Docker and cloud credentials
- **`databao ask`** — requires OpenAI API key

Never add these to pre-commit hooks or CI without explicit team decision.

## Coverage

Unit test coverage is measured with `pytest-cov` and enforced at the threshold
set in `[tool.coverage.report] fail_under` in `pyproject.toml`.

Configuration lives in `pyproject.toml` under `[tool.coverage.*]` sections.

**What to cover**: CLI commands, MCP tools, query execution, datasource checks,
project management, and utility functions.

**What is excluded**: Streamlit UI (`src/databao_cli/ui/`) and the
`__main__.py` entrypoint wrapper are excluded from unit coverage.

**When coverage drops**: See the `check-coverage` skill for the decision
procedure on whether to fix code or fix tests. Use the `write-tests` skill
for guidance on writing new tests that follow project conventions.

## Agent Behavior

Agents should **always** run verification locally:

- After any code change, run at minimum `make check` and the relevant unit
  tests before considering the change complete.
- Run `uv run databao --help` after modifying CLI entrypoints, commands, or
  top-level imports.
- If a test fails, diagnose and fix — do not skip or ignore failures.
- If the environment is not set up, run `make setup` rather than falling
  back to a smoke-test-only mode.
- Run full `make test` before finalizing larger changes that touch multiple
  modules.
- After code changes, run `make test-cov-check` to verify coverage ≥80%.
