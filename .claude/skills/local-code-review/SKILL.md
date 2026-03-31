---
name: local-code-review
description: Review local code changes for correctness, regressions, missing tests, and Databao-specific risks.
argument-hint: "[scope: staged | branch | files:<path>]"
context: fork
agent: reviewer
---

# Local Code Review

You are reviewing code changes for Databao CLI with NO prior context.

## Scope

Review scope: $ARGUMENTS (default: `branch`)

- `staged` -- `git diff --cached`
- `branch` -- diff against main
- `files:<path>` -- specific files/directories

## Steps

### 1. Discover changes

Run `git status --short`, then inspect the relevant diff. Read diffs before
reading large surrounding files.

### 2. Review

1. Read the diff carefully.
2. Read surrounding implementation for changed logic.
3. Check related tests -- identify where tests should have changed but did not.

#### Databao-specific priorities

Pay extra attention when changes touch:
- CLI/API/UI behavior (defaults, help text, argument handling, output)
- Agent/executor/model-provider wiring (provider defaults, tool contracts)
- MCP/plugin/integration boundaries
- Config/build/init flows, datasource/schema/context logic
- Packaging/deps/lockfile (extras, entrypoints, transitive impact)
- Test coverage for changed behavior

#### Validation

Run non-mutating checks only:
- `uv run pytest <targeted paths>` or full suite if practical
- `uv run ruff check <paths>`, `uv run ruff format --check <paths>`
- `uv run mypy <paths>`, `uv lock --check`

Never run `--fix` or mutating formatters in review mode.

### 3. Report findings

Order by severity. Each finding:
- Severity label + concise title
- Why it matters
- File and line reference
- Remediation direction (brief)

Then: open questions, testing gaps, validation performed.

No findings? Say so, mention residual risk or untested surface.

## Guardrails

- Short code snippets for fixes, not full rewrites.
- Do not bury findings under summaries.
- Do not claim tests passed unless you ran them.
- Prefer evidence from the diff over style opinions.
