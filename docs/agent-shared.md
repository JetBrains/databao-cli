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

- Environment setup: `make setup` (installs deps, pre-commit hooks, verifies toolchain)
- Pre-commit (ruff + mypy): `make check` or `uv run pre-commit run --all-files`
- Ruff lint: `uv run ruff check src/databao_cli`
- Ruff format: `uv run ruff format src/databao_cli`
- Mypy: `uv run mypy src/databao_cli`
- Unit tests: `make test` or `uv run pytest tests/ -v`
- E2E tests: `make e2e-test` or `uv run --group e2e-tests pytest e2e-tests`
- Smoke test: `uv run databao --help`
- Single test file: `uv run pytest tests/test_foo.py -v`
- Single test: `uv run pytest tests/test_foo.py::test_bar -v`
- Coverage check: `make test-cov-check` (fails if below 80%)
- Coverage report: `make test-cov` (terminal + HTML in `htmlcov/`)
- Skill validation: `make lint-skills` (static checks on agent guidance)
- Skill smoke tests: `make smoke-skills` (functional verification of skill commands)

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
- Run `make test-cov-check` after changing code in `src/databao_cli/` to
  verify coverage ≥80%. If existing tests break, fix the production code —
  do not weaken tests. If newly written tests are wrong, fix the tests.
- Agent context files (`CLAUDE.md`, `.cursorrules`) are auto-synced on commit
  via pre-commit hook. Run `scripts/sync-agent-context.sh` manually if you
  need updated context mid-session.
- When modifying agent guidance files (skills, `docs/agent-shared.md`,
  coding-guidelines), run `make lint-skills` to validate consistency.
  The pre-commit hook runs this automatically on commit.

## YouTrack Ticket Workflow

- Before starting work, ask for a YouTrack ticket ID (e.g., `DBA-123` or just
  `123` — expand bare numbers to `DBA-123`).
- If the YouTrack MCP server is unavailable, refer the user to `DEVELOPMENT.md`
  for setup instructions.
- If a ticket is provided, read it with the `get_issue` tool to understand the
  full scope before writing any code.
- If no ticket exists for the work, propose one (show summary, description, and
  type) and wait for explicit user approval before creating it.
- When starting work on a ticket, move it to **Develop** state using
  `update_issue` (set `State` field).
- After creating a PR, move the ticket to **Review** state and add the
  PR URL as a comment.
- Prefix every commit message with the ticket ID:
  `[DBA-123] Description of change`.

## After Completing Work

1. **Test & lint** — run `make check` then `make test-cov-check`. Fix any
   failures before proceeding.
2. **Architecture review** — run the `review-architecture` skill on the
   changed code. Fix any High-severity issues it raises.
3. **Branch** — create a branch following `<nickname>/<descriptive-branch-name>`.
   Detect the user's nickname from existing remote branches:
   ```bash
   git branch -r | sed -nE 's|^ *origin/([^/]+)/.*|\1|p' | grep -vE '^(dependabot|HEAD|revert-)' | sort | uniq -c | sort -rn
   ```
4. **Commit** — stage and commit with `[DBA-123] Description of change`.
5. **Pause** — present the user with a summary of what will be pushed and
   the draft PR description. Wait for explicit confirmation before
   proceeding.
6. **Push & PR** — push with `-u` flag, create PR using the standard
   format (see Pull Request Format section).
7. **Update YouTrack** — move the ticket to **Review** state and add
   a comment with the PR URL.
8. Never commit directly to `main`.

## Pull Request Format

Use the following structure for PR descriptions:

```
## Summary
<1–3 sentence overview of why this change exists>

## Changes

### <Logical change 1>
<Brief description>
<details><summary>Files</summary>

- `path/to/file1`
- `path/to/file2`
</details>

### <Logical change 2>
...

## Test Plan
- [ ] <Step or check to verify correctness>
```
