# Setup Environment

Set up or verify the local development environment so that lint, type-check,
and tests can run.

## When to use

- Starting work in a fresh clone or new machine.
- A command fails with missing dependencies or broken imports.
- Before running `make check` or `make test` for the first time in a session.

## Steps

Run these commands in order. Stop and diagnose if any step fails.

### 1. Check prerequisites

Verify that required tools are available:

```bash
python3 --version   # must be >=3.11
uv --version        # must be installed
git --version       # must be installed
```

If `uv` is missing, install it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Install dependencies

```bash
uv sync --dev
```

This installs all runtime and development dependencies (ruff, mypy, pytest,
pre-commit, etc.) into a local virtualenv managed by `uv`.

### 3. Install pre-commit hooks

```bash
uv run pre-commit install
```

### 4. Verify the environment

Run these checks to confirm everything works:

```bash
uv run databao --help                         # CLI entrypoint loads
uv run ruff check src/databao_cli             # linter runs
uv run mypy src/databao_cli                   # type-checker runs
uv run pytest tests/ -v --co                  # test collection succeeds
```

### 5. Report

After all steps pass, report:

- Python version
- `uv` version
- Number of dependencies installed
- Number of tests collected
- Any warnings or skipped checks

## Failure handling

- If `python3 --version` reports < 3.11, stop and tell the user to install a
  supported Python version.
- If `uv sync --dev` fails, check for conflicting lockfiles or network issues
  and report the error.
- If the smoke test (`databao --help`) fails, there is likely a broken import —
  diagnose before proceeding with any other work.

## What this skill does NOT do

- It does not run the full test suite — use `make test` for that.
- It does not configure cloud credentials or Docker for E2E tests.
- It does not modify `pyproject.toml` or add new dependencies.
