# Copilot Custom Instructions

Instructions for GitHub Copilot when reviewing pull requests in this repository.

## Project Context

This is a Python CLI tool (`databao`) built with Click. Main code lives in
`src/databao_cli/`. Tests live in `tests/`. Deps managed by `uv` +
`pyproject.toml`. Strict mypy is enabled.

## Code Review Checklist

When reviewing a PR, check each of the following areas and flag violations.

### Commit Hygiene

- When a YouTrack ticket exists:
  - The PR title SHOULD include the ticket ID as a `[DBA-XXX]` prefix (e.g.,
    `[DBA-123] add datasource validation`).
  - The branch name SHOULD include the bare ticket ID `DBA-XXX` somewhere in
    the name (e.g., `<nickname>/DBA-123-fix-auth-timeout`).
  - If commit messages are visible in the review context, they SHOULD also
    include the `[DBA-XXX]` prefix.
- Do NOT require or flag a missing `[DBA-XXX]` prefix when no ticket exists.

### Code Correctness

Ensure the coding guidelines specified under `docs/python-coding-guidelines.md` are followed.

### Architecture

Understand the project architecture described in `docs/architecture.md` and enforce consistency.

### Test Coverage

- If the PR changes behavior in files under `src/databao_cli/`, check that
  corresponding test files under `tests/` are also modified or added.
- New CLI commands, MCP tools, and utility functions MUST have unit tests.
- Bug fixes SHOULD include a regression test.
- Flag PRs that change behavior in production code but add zero test changes.
  Pure refactors, formatting-only, or comment-only changes do not require new
  tests.
- Do NOT require new tests for purely cosmetic or layout-only changes to
  Streamlit UI components under `src/databao_cli/ui/` that do not alter
  control flow or data handling.
- Changes to `src/databao_cli/__main__.py` that alter CLI behavior, commands,
  or options SHOULD have corresponding tests. Wiring-only refactors with
  identical behavior do not require new tests.

### Documentation

- If a PR adds or changes a CLI command, check that `README.md` command
  examples and usage sections are updated accordingly.
- If a PR changes user-visible behavior (new flags, changed defaults, removed
  options), check that help text in the Click decorators reflects the change.
- If a PR adds or modifies an MCP tool, check that docstrings describe
  parameters and return values.
- Flag PRs with user-facing changes but no documentation updates.

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
