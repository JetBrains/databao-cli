---
name: review-architecture
description: Review architecture quality, maintainability, and developer experience before or after significant changes. Use when introducing a new CLI command or MCP tool, refactoring core module boundaries, diagnosing repeated dev friction, or preparing a PR with broad structural impact.
---

# Review Architecture

Review architecture quality, maintainability, and developer experience (Dev UX)
before or after significant changes.

## Primary sources of truth

Review in this order:

1. `docs/architecture.md`
2. `docs/python-coding-guidelines.md`
3. `docs/testing-strategy.md`
4. `CLAUDE.md`
5. `README.md` (CLI usage and user-facing workflows)

## Review goals

- Confirm boundaries are clear and responsibilities are separated.
- Confirm extension paths are low-friction (new command, MCP tool, UI page).
- Confirm docs reflect real behavior and command paths.
- Identify highest-impact improvements with minimal disruption.

## Architecture checklist

- Are modules aligned with single responsibility?
- Are CLI concerns separated from business logic?
- Is the Click command structure clean and discoverable?
- Does `workflows/` stay free of business logic (delegates to `features/`)?
- Are `features/` functions free of Click dependency (pure business operations)?
- Is `shared/` limited to cross-feature utilities with no business logic of its own?
- Are MCP tools properly isolated in their own module?
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
