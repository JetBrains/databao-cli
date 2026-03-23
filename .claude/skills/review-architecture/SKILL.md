---
name: review-architecture
description: Review architecture quality, maintainability, and developer experience before or after significant changes. Use when introducing a new CLI command or MCP tool, refactoring core module boundaries, diagnosing repeated dev friction, or preparing a PR with broad structural impact.
argument-hint: "[scope: branch | module:<path> | full]"
context: fork
agent: general-purpose
---

# Review Architecture

You are reviewing the architecture of the Databao CLI project.
You have NO prior context about why these changes were made — review
purely on merit. Use your tools (Read, Grep, Glob, Bash) to inspect
the code and project structure. Do NOT edit any files.

## Scope

Review scope: $ARGUMENTS

If no scope was provided, default to `branch`.

Accepted scopes:

- `branch` — review architecture of code changed on the current branch (default)
- `module:<path>` — review a specific module (e.g. `module:src/databao_cli/mcp/`)
- `full` — review the full project architecture

## Primary sources of truth

Review in this order:

1. `docs/architecture.md`
2. `docs/python-coding-guidelines.md`
3. `docs/testing-strategy.md`
4. `CLAUDE.md`
5. `README.md` (CLI usage and user-facing workflows)

Then validate actual implementation under:

- `src/databao_cli/commands/`
- `src/databao_cli/ui/`
- `src/databao_cli/mcp/`
- `src/databao_cli/project/`

## Review goals

- Confirm boundaries are clear and responsibilities are separated.
- Confirm extension paths are low-friction (new command, MCP tool, UI page).
- Confirm docs reflect real behavior and command paths.
- Identify highest-impact improvements with minimal disruption.

## Architecture checklist

- Are modules aligned with single responsibility?
- Are CLI concerns separated from business logic?
- Is the Click command structure clean and discoverable?
- Are MCP tools properly isolated in `mcp/tools/`?
- Are UI components reusable and page-specific logic separated?
- Are errors actionable and surfaced at the right layer?

## Dev UX checklist

- Can a new contributor find the right entrypoints quickly?
- Are `uv` / `make` commands obvious and consistent across docs/code?
- Is local verification clear (`make check`, `make test`)?
- Are defaults safe when environment/dependencies are missing?
- Do naming and file layout reduce cognitive load?
- Are common workflows discoverable in README + docs?

## Output format

Provide a concise report with these sections:

1. **Current State**: 3-6 bullets on what is working well.
2. **Risks / Gaps**: prioritized issues (High/Med/Low) with evidence.
3. **Recommendations**: concrete changes, ordered by impact vs effort.
4. **Doc Sync Needed**: exact files that should be updated.
5. **Validation Plan**: minimal commands to verify proposed changes.

## Recommendation style

- Prefer small, composable changes over sweeping rewrites.
- Tie every recommendation to a specific pain point.
- Include expected developer benefit (speed, clarity, reliability).
- Flag trade-offs explicitly.
- Separate immediate actions from longer-term improvements.

## Guardrails

- Do not invent architecture that conflicts with current code unless proposing it
  explicitly as a future direction.
- Do not request broad rewrites without clear ROI.
- Keep proposals compatible with existing `uv` workflow and Click-based CLI.
- Keep feedback actionable for the next pull request, not just aspirational.
