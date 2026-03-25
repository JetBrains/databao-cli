# Copilot Custom Instructions

Instructions for GitHub Copilot when reviewing pull requests in this repository.

## Project Context

This is a Python CLI tool (`databao`) built with Click. Main code lives in
`src/databao_cli/`. Tests live in `tests/`. Deps managed by `uv` +
`pyproject.toml`. Strict mypy is enabled.

## Code Review Checklist

When reviewing a PR, check each of the following areas and flag violations.

### Commit Hygiene

- When a YouTrack ticket exists, the PR title and/or branch name SHOULD
  include the ticket ID in the format `[DBA-XXX]` (e.g., `[DBA-123] add
  datasource validation`). If commit messages are visible in the review
  context, they SHOULD also include this prefix.
- Do NOT require or invent a `[DBA-XXX]` prefix when no ticket exists. Do not
  flag commits or PRs that lack this prefix if there is no associated ticket.

### Test Coverage

- If the PR changes behavior in files under `src/databao_cli/`, check that
  corresponding test files under `tests/` are also modified or added.
- New CLI commands, MCP tools, and utility functions MUST have unit tests.
- Bug fixes SHOULD include a regression test.
- Flag PRs that change behavior/commands/protocols in production code but
  add zero test changes. Pure refactors, formatting-only, or comment-only
  changes do not require new tests.
- Do NOT require tests for changes to `src/databao_cli/ui/` (Streamlit UI)
  or `src/databao_cli/__main__.py` (wiring-only entrypoint).

### Documentation

- If a PR adds or changes a CLI command, check that `README.md` command
  examples and usage sections are updated accordingly.
- If a PR changes user-visible behavior (new flags, changed defaults, removed
  options), check that help text in the Click decorators reflects the change.
- If a PR adds or modifies an MCP tool, check that docstrings describe
  parameters and return values.
- Flag PRs with user-facing changes but no documentation updates.

### Code Correctness (from project coding guidelines)

- **Error handling**: No blanket `except Exception` / `except BaseException`
  without re-raise, except at MCP tool boundaries where structured error JSON
  is returned. Catch narrow, specific exceptions.
- **CLI layer**: `__main__.py` should contain only command registrations and
  delegation to `*_impl()` functions — no business logic.
- **Type hints**: Public functions must have full type signatures. Use
  `X | None` not `Optional[X]`.
- **Imports**: No import-time side effects. Heavy imports (Streamlit, ML libs)
  must be lazy (inside functions).
- **Data modeling**: Use dataclasses for internal state, Pydantic for
  validation boundaries (API/MCP). No raw `dict` for structured data passed
  between functions.
- **Path handling**: Use `pathlib.Path`, not `os.path`.
- **User output**: CLI uses `click.echo` / `click.secho`, not `print`.
- **Mutable defaults**: Must use `field(default_factory=...)`, never mutable
  literals as defaults.

### Architecture

- CLI commands delegate to `*_impl()` in their respective modules under
  `commands/`. Flag logic creeping into `__main__.py`.
- MCP tools live in `src/databao_cli/mcp/tools/` with a
  `register(mcp, context)` pattern. Flag tools defined outside this structure.
- New commands must validate project state early using
  `ProjectLayout` + `databao_project_status()` before doing work.
- Flag broad exception swallowing that hides failure modes.

### Dependencies and Packaging

- All dependencies must be declared in `pyproject.toml`. Flag any
  `requirements.txt`, `setup.py`, or other non-standard dep files.
- Check that optional dependency groups (extras) are wired correctly if
  the PR adds new database support or heavy optional deps.
- Flag lockfile (`uv.lock`) changes that look unrelated to the PR's intent.

### Security

- No secrets, API keys, or credentials in code or config files.
- No logging of secrets.
- Validate user input at system boundaries.