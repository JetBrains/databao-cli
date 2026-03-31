# CLAUDE.md

Claude Code entrypoint for agent instructions in this repository.

## Agent Delta (Claude Code)

- Prefer concise updates with clear file/command references.
- YouTrack MCP must be configured (see DEVELOPMENT.md). Use get_issue / update_issue tools.
- **Pacing rule**: pause for user confirmation between phases (plan →
  implement → validate → commit → PR). Small, safe actions within a phase
  do not require a pause.
  - **Exception — autosteer mode**: skip all inter-phase confirmations.
    Stop only on quality-gate failures.

## Output Efficiency

- No sycophantic openers ("Sure!", "Great question!", "Absolutely!") — lead with the answer.
- No hollow closings ("Let me know if you need anything!", "I hope this helps!").
- No restating the user's prompt — execute immediately.
- No unsolicited suggestions or scope creep — answer exact scope only.
- No redundant file reads — read each file once per session unless changed.
- No unnecessary disclaimers unless there is a genuine safety risk.
- When corrected, apply the correction as ground truth — no "You're absolutely right" preamble.
- Code first, explanation after — only if non-obvious. No inline prose in code blocks.
- Simplest working solution. No abstractions for single-use operations.
- ASCII-only output: plain hyphens, straight quotes. Copy-paste safe.

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

- Setup: `make setup`
- Lint + type-check: `make check`
- Unit tests: `make test`
- Single test: `uv run pytest tests/test_foo.py::test_bar -v`
- Coverage check: `make test-cov-check` (fails if below 80%)
- Coverage report: `make test-cov` (HTML in `htmlcov/`)
- Skill validation: `make lint-skills`

### Quality Gates

These three gates are **blocking** before any commit. Skills reference
this section instead of repeating the commands.

1. `make check` — ruff + mypy. Auto-fix ruff with `uv run ruff check --fix src/databao_cli && uv run ruff format src/databao_cli`, then re-run.
2. `make test` — pytest. Fix failures before continuing.
3. `make test-cov-check` — coverage threshold. Write tests if below 80%.

## Coding Guidelines

Style enforced by ruff + mypy. Use `ruff check --fix` and `ruff format` to auto-fix.

- Type hints on public APIs; strict mypy enabled.
- Validate config/args early; raise specific exceptions.
- Use `logging` for runtime; `print` only for tiny utilities.
- CLI framework is Click.

## Change Management

- Minimal, focused edits over broad rewrites.
- Update tests when changing commands, protocols, or behavior.
- Update `README.md` if command examples or workflows change.
- Run `make test-cov-check` after changing `src/databao_cli/`. If existing
  tests break, fix production code -- do not weaken tests.
- Run `make lint-skills` after modifying agent guidance files.

## YouTrack Ticket Workflow

- Use `make-yt-issue` skill to verify or create a ticket before starting work.
- Read ticket with `get_issue` to understand scope before coding.
- Move to **Develop** on start (`update_issue`, set `State`).
- Move to **Review** after PR, comment with PR URL and session cost (`/cost`).
- If YouTrack MCP unavailable, refer user to `DEVELOPMENT.md`.

## Commit Messages

- Format: `[DBA-XXX] <imperative summary>` (max 72 chars)
- Imperative mood, lowercase after prefix: `[DBA-123] fix auth timeout`
- No trailing period. Body explains *why*, not *what*. Wrap at 72 chars.
- No ticket? Omit the prefix.

## After Completing Work

Each step is a **phase** -- pause for confirmation between phases (except in autosteer mode).

1. **Plan** -- outline approach and files to change.
2. **Implement** -- code + tests. Run `make test`.
3. **Validate** -- run quality gates (see above). Fix failures.
4. **Review** -- run `local-code-review` and `review-architecture` skills in parallel (forked context).
5. **Branch & commit** -- `create-branch` skill, then commit per **Commit Messages**.
6. **PR** -- `create-pr` skill.
7. **Update YouTrack** -- move to **Review**, comment with PR URL + session cost (`/cost`).

Never commit directly to `main`.
