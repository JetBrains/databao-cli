---
name: setup-environment
description: Set up or verify the local development environment. Use when starting work in a fresh clone, when commands fail with missing dependencies, or before running checks for the first time.
disable-model-invocation: true
---

# Setup Environment

Set up or verify the local development environment.

## When to use

- Starting work in a fresh clone or new machine.
- A command fails with missing dependencies or broken imports.
- Before running `make check` or `make test` for the first time in a session.

## Steps

### 1. Run setup

```bash
make setup
```

This installs all dependencies, pre-commit hooks, and verifies that the
linter, type-checker, CLI entrypoint, and test collection all work.

### 2. If setup fails, diagnose

- **`python3 --version` reports < 3.11** — ask the user to install a
  supported Python version.
- **`uv` not found** — install it: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **`uv sync --dev` fails** — check for conflicting lockfiles or network
  issues and report the error.
- **`databao --help` fails** — broken import; diagnose before proceeding
  with any other work.
- **Lint / type-check / test collection fails** — likely a code issue, not
  an environment issue. Investigate the specific error.

## What this skill does NOT do

- Run the full test suite — use `make test` for that.
- Configure cloud credentials or Docker for E2E tests.
- Modify `pyproject.toml` or add new dependencies.
