# Coding Guidelines

Practical coding rules for contributors and coding agents.
Style and formatting are enforced by ruff and mypy — these guidelines cover
only what linters cannot catch.

## Language and Tooling

- Python version target: see `requires-python` in `pyproject.toml`.
- Dependency/runtime management: `uv` + `pyproject.toml`.
- Run project commands through `uv run`.
- Local install/update: `make setup` (or `uv sync --dev` for deps only)
- Do not introduce ad-hoc dependency files (`requirements.txt`, etc.) unless
  explicitly requested.

## Required Quality Commands

Run the narrowest relevant command first, then broaden scope.

- Pre-commit (ruff + mypy): `make check`
- Ruff lint: `uv run ruff check src/databao_cli`
- Ruff format: `uv run ruff format src/databao_cli`
- Ruff auto-fix: `uv run ruff check --fix src/databao_cli`
- Mypy: `uv run mypy src/databao_cli`
- Unit tests: `make test`
- E2E tests: `make e2e-test`
- Coverage check: `make test-cov-check`
- Single test file: `uv run pytest tests/test_foo.py -v`
- Single test function: `uv run pytest tests/test_foo.py::test_bar -v`

Use `ruff check --fix` and `ruff format` to auto-fix style issues — do not
manually fix formatting or linter-enforceable style.

## General Coding Style

- Prefer readability over clever/compact tricks.
- Keep functions focused; extract helpers for repeated logic.
- Avoid large refactors when a targeted fix is sufficient.

## Comments and Docstrings

- Do not leave inline comments explaining obvious code behavior.
- Do write docstrings for modules, classes, and functions where it adds clarity.

## Imports

- Avoid import-time side effects.

## Typing and Data Models

- Strict mypy is enabled — add type hints to all public APIs and non-trivial helpers.
- Use Pydantic models or `@dataclass` for structured payloads.
- SQLAlchemy and Pydantic mypy plugins are active.

## Error Handling and Validation

- Validate config/arguments early, before expensive runtime work.
- Use specific exceptions:
  - `FileNotFoundError` for missing files/directories
  - `ValueError` for invalid values or argument combinations
  - `RuntimeError` for runtime state failures
  - `click.UsageError` for CLI input errors
- Make errors actionable; include the problematic value/path.

## Logging and Output

- Use `logging` for runtime behavior and diagnostics.
- LLM-specific error handling lives in `src/databao_cli/log/llm_errors.py`.
- Use `print` only for tiny scripts/utilities where logging is unnecessary.
- Click's `echo`/`secho` is preferred for CLI user output.

## CLI Patterns

- All commands use Click decorators (`@click.command`, `@click.group`).
- Global options (`-v`, `-p`) are on the top-level group in `__main__.py`.
- Register new commands in the Click group in `__main__.py`.
- Use Click's built-in validation (types, callbacks) over manual parsing.
- Keep CLI flags stable and intuitive (Click conventions).

## Testing Guidance

- Add/adjust tests when changing behavior, commands, or interfaces.
- Prefer small focused unit tests near changed behavior.
- For bug fixes, include at least one regression test when feasible.
- E2E tests use `pexpect`, `testcontainers`, and `allure-pytest`.

## Anti-Patterns to Avoid

- Large unrelated rewrites in focused change requests.
- Silent behavior changes without docs/tests updates.
- Broad catch-all exception handling that hides root causes.
