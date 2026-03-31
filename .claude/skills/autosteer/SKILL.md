---
name: autosteer
description: Run the full development pipeline autonomously without pausing between phases. Stops only on quality-gate failures.
argument-hint: "[ticket-id-or-task-description]"
---

# Autosteer

Suspends the **pacing rule** from `CLAUDE.md`. Proceed through all phases
without confirmation, stopping **only** on quality-gate failures.

## Activation

- Do **not** pause between phases or present plans for approval.
- **Do** stop on quality-gate failure (`make check`, `make test`,
  `make test-cov-check`). Attempt fix twice, then stop and report.

## Steps

### 1. Resolve the ticket

If argument is a ticket ID (`DBA-XXX`, number, or URL): fetch with
`get_issue`, move to **Develop**.

If free-text: create via `create_issue` in **DBA** project (derive
summary, description, type; default Task). Move to **Develop**.

If no argument: ask user once, then proceed autonomously.

### 2. Execute phases

Follow **After Completing Work** in `CLAUDE.md` (phases 1-7), with:
- Phase 2 (implement): up to two retries on test failure.
- Phase 3 (validate): run quality gates per **Quality Gates** in `CLAUDE.md`.
  Two fix attempts, then stop.
- Phase 4 (review): fix Critical/High findings, note Medium/Low.
- Phase 5-7: use `create-branch`, `create-pr` skills. Skip pre-push pause.

### 3. Report

Output: ticket ID/link, branch name, PR URL, unfixed review findings.

## Guardrails

- Never commit or push to `main`.
- Never skip quality gates.
- Never create a ticket without at least a task description.
- Stage specific files -- never `git add -A` or `git add .`.
- If `gh` or YouTrack MCP unavailable, stop and inform user.
