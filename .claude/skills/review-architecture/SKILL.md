---
name: review-architecture
description: Review architecture quality, maintainability, and developer experience.
argument-hint: "[scope: branch | module:<path> | full]"
context: fork
agent: reviewer
---

# Review Architecture

You are reviewing Databao CLI architecture with NO prior context.

## Scope

Review scope: $ARGUMENTS (default: `branch`)

- `branch` -- architecture of code changed on current branch
- `module:<path>` -- specific module
- `full` -- full project architecture

## Sources of truth

1. `docs/architecture.md`
2. `docs/python-coding-guidelines.md`
3. `docs/testing-strategy.md`
4. `CLAUDE.md`
5. `README.md`

## Architecture checklist

- Modules aligned with single responsibility?
- CLI concerns separated from business logic?
- Click command structure clean and discoverable?
- `workflows/` delegates to `features/`, no business logic?
- `features/` free of Click dependency?
- `shared/` limited to cross-feature utilities?
- MCP tools properly isolated?
- Errors actionable and surfaced at right layer?

## Dev UX checklist

- New contributors find entrypoints quickly?
- `uv`/`make` commands obvious and consistent?
- Defaults safe when deps missing?
- Naming and layout reduce cognitive load?

## Output format

1. **Current State**: 3-6 bullets on what works well
2. **Risks/Gaps**: prioritized (High/Med/Low) with evidence
3. **Recommendations**: concrete, ordered by impact vs effort
4. **Doc Sync**: files needing updates
5. **Validation Plan**: commands to verify changes

## Guardrails

- Small composable changes over rewrites. Tie recommendations to pain points.
- Keep proposals compatible with `uv` workflow and Click CLI.
- Actionable for next PR, not aspirational.
