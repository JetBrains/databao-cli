# Agent Shared Core

Shared operating context for all coding agents in this repository.

## Project Scope

- Applies to the full repository rooted at `.`.
- Main code lives in `src/databao_cli/`.
- This is a Python CLI tool for interacting with the Databao Agent and
  Databao Context Engine. Published on PyPI as `databao`.
- CLI entry point: `databao` command (Click-based).

## Repo Snapshot

- Dependency management: `pyproject.toml` + `uv`
- Build backend: `hatchling` + `uv-dynamic-versioning` (git tags)
- Dev tools: `ruff`, `mypy`, `pytest`, `pre-commit`
- Unit tests in `tests/`, end-to-end tests in `e2e-tests/`

Key directories:

- `src/databao_cli/commands/`: CLI command implementations (`init`, `ask`, `build`, `status`, `app`, `mcp`, `datasource/`)
- `src/databao_cli/ui/`: Streamlit web UI (pages, components, services, models)
- `src/databao_cli/mcp/`: Model Context Protocol server and tools
- `src/databao_cli/project/`: project layout and management
- `src/databao_cli/log/`: logging configuration and LLM error handling
- `examples/`: example projects (e.g., `demo-snowflake-project`)

## Environment Defaults

- Python `>=3.11`
- Install deps: `uv sync --dev`
- Run commands with `uv run`

## Build, Lint, Test Commands

- Pre-commit (ruff + mypy): `make check` or `uv run pre-commit run --all-files`
- Ruff lint: `uv run ruff check src/databao_cli`
- Ruff format: `uv run ruff format src/databao_cli`
- Mypy: `uv run mypy src/databao_cli`
- Unit tests: `make test` or `uv run pytest tests/ -v`
- E2E tests: `make e2e-test` or `uv run --group e2e-tests pytest e2e-tests`
- Smoke test: `uv run databao --help`
- Single test file: `uv run pytest tests/test_foo.py -v`
- Single test: `uv run pytest tests/test_foo.py::test_bar -v`

## Coding Guidelines

- Imports grouped as stdlib, third-party, local (`databao_cli.*`) with blank lines.
- 4-space indentation; line length target 127 (ruff config).
- Add type hints for public APIs and non-trivial helpers; strict mypy is enabled.
- Prefer modern generics (`list[str]`, `dict[str, Any]`).
- Naming: `snake_case` functions/modules, `PascalCase` classes,
  `UPPER_SNAKE_CASE` constants.
- Validate config/args early and raise specific exceptions with actionable
  messages.
- Use `logging` for runtime behavior; use `print` only for tiny utilities.
- CLI framework is Click — follow Click patterns for new commands.
- Prefer absolute imports (`TID252` rule enforced by ruff).

## Change Management

- Prefer minimal, focused edits over broad rewrites.
- Do not silently alter behavior; document intentional changes.
- Update tests when changing commands, protocols, or behavior.
- Update `README.md` if command examples or workflows change.
