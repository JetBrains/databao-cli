# CLAUDE.md

Claude Code entrypoint for agent instructions in this repository.

## Agent Delta (Claude Code)

- Prefer concise updates with clear file/command references.
- Execute directly when safe; ask questions only if truly blocked.
- YouTrack MCP must be configured (see DEVELOPMENT.md). Use get_issue / update_issue tools.

## References

- `docs/architecture.md`
- `docs/coding-guidelines.md`
- `docs/testing-strategy.md`

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
- Unit tests in `tests/`

Key directories:

- `src/databao_cli/commands/`: CLI command implementations (`init`, `ask`, `build`, `status`, `app`, `mcp`, `datasource/`)
- `src/databao_cli/ui/`: Streamlit web UI (pages, components, services, models)
- `src/databao_cli/mcp/`: Model Context Protocol server and tools
- `src/databao_cli/project/`: project layout and management
- `src/databao_cli/log/`: logging configuration and LLM error handling
- `examples/`: example projects (e.g., `demo-snowflake-project`)

## Environment Defaults

- Python version: see `requires-python` in `pyproject.toml`.
- Install deps: `uv sync --dev`
- Run commands with `uv run`

## Build, Lint, Test Commands

- Environment setup: `make setup` (installs deps, pre-commit hooks, verifies toolchain)
- Pre-commit (ruff + mypy): `make check` or `uv run pre-commit run --all-files`
- Ruff lint: `uv run ruff check src/databao_cli`
- Ruff format: `uv run ruff format src/databao_cli`
- Mypy: `uv run mypy src/databao_cli`
- Unit tests: `make test` or `uv run pytest tests/ -v`
- Smoke test: `uv run databao --help`
- Single test file: `uv run pytest tests/test_foo.py -v`
- Single test: `uv run pytest tests/test_foo.py::test_bar -v`
- Coverage check: `make test-cov-check` (fails if below 80%)
- Coverage report: `make test-cov` (terminal + HTML in `htmlcov/`)
- Skill validation: `make lint-skills` (static checks on agent guidance)
- Skill smoke tests: `make smoke-skills` (functional verification of skill commands)

## Coding Guidelines

Style and formatting are enforced by ruff and mypy — only non-linter-enforceable
rules are listed here. Use `ruff check --fix` and `ruff format` to auto-fix
style issues; do not manually fix formatting.

- Add type hints for public APIs and non-trivial helpers; strict mypy is enabled.
- Validate config/args early and raise specific exceptions with actionable
  messages.
- Use `logging` for runtime behavior; use `print` only for tiny utilities.
- CLI framework is Click — follow Click patterns for new commands.

## Change Management

- Prefer minimal, focused edits over broad rewrites.
- Do not silently alter behavior; document intentional changes.
- Update tests when changing commands, protocols, or behavior.
- Update `README.md` if command examples or workflows change.
- Run `make test-cov-check` after changing code in `src/databao_cli/` to
  verify coverage meets the threshold in `[tool.coverage.report] fail_under`
  (`pyproject.toml`). If existing tests break, fix the production code —
  do not weaken tests. If newly written tests are wrong, fix the tests.
- When modifying agent guidance files (skills, coding-guidelines),
  run `make lint-skills` to validate consistency.
  The pre-commit hook runs this automatically on commit.

## YouTrack Ticket Workflow

- Before starting work, use the `make-yt-issue` skill to verify or create a
  YouTrack ticket. It handles asking for the ID, validating it exists, and
  creating one if needed.
- If the YouTrack MCP server is unavailable, refer the user to `DEVELOPMENT.md`
  for setup instructions.
- If a ticket is provided, read it with the `get_issue` tool to understand the
  full scope before writing any code.
- When starting work on a ticket, move it to **Develop** state using
  `update_issue` (set `State` field).
- After creating a PR, move the ticket to **Review** state and add a
  comment with the PR URL and the Claude Code session cost (from `/cost`).
## Commit Messages

- Format: `[DBA-XXX] <imperative summary>` (max 72 chars)
- Use imperative mood: "Add feature", not "Added feature" or "Adds feature"
- Lowercase after the prefix: `[DBA-123] fix auth timeout`
- No trailing period
- If a body is needed, add a blank line after the summary:
  - Explain *why*, not *what* (the diff shows what)
  - Wrap at 72 characters
- If no ticket exists, omit the prefix — don't invent one

## After Completing Work

1. **Implement** — write the code changes to satisfy the ticket
   requirements.
2. **Write tests** — add or update unit tests covering the new behavior;
   run `make test` to verify they pass.
3. **Test & lint** — run `make check` then `make test-cov-check`. Fix any
   failures before proceeding.
4. **Review the code** — review the code locally. Fix any high-severity
   findings before proceeding.
5. **Architecture review** — review architecture quality of the changed
   code. Fix any high-severity issues before proceeding.
6. **Branch** — use the `create-branch` skill.
7. **Commit & PR** — use the `create-pr` skill (stages, commits, pauses
   for confirmation, pushes, and opens the PR).
8. **Update YouTrack** — move the ticket to **Review** state and add
   a comment with the PR URL and the Claude Code session cost (run
   `/cost` to obtain it).
9. Never commit directly to `main`.
