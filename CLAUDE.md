# CLAUDE.md

Claude Code entrypoint for agent instructions in this repository.

## Agent Delta (Claude Code)

- Prefer concise updates with clear file/command references.
- YouTrack MCP must be configured (see DEVELOPMENT.md). Use get_issue / update_issue tools.
- **Pacing rule**: pause for user confirmation between phases (plan →
  implement → validate → commit → PR). Present what you intend to do or
  what you just did, then wait for a go-ahead before moving to the next
  phase. Small, safe actions within a phase (running tests, reading files)
  do not require a pause.

## References

- `docs/architecture.md`
- `docs/python-coding-guidelines.md`
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

Each numbered step below is a **phase**. Present the outcome of each
phase and wait for user confirmation before starting the next one.

1. **Plan** — outline the approach and list files you intend to change.
2. **Implement** — write the code changes to satisfy the ticket
   requirements, including tests. Run `make test` to verify they pass.
3. **Validate** — run `make check` then `make test-cov-check`. Fix any
   failures before proceeding.
4. **Review** — run `local-code-review` and `review-architecture` skills.
   Both run in forked sub-agent context (no prior conversation state)
   and can run **in parallel**.
5. **Branch & commit** — use the `create-branch` skill, then stage and
   commit following **Commit Messages** conventions.
6. **PR** — use the `create-pr` skill (pushes and opens the PR).
7. **Update YouTrack** — move the ticket to **Review** state and add
   a comment with the PR URL and the Claude Code session cost (run
   `/cost` to obtain it).

Never commit directly to `main`.
