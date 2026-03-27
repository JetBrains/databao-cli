---
name: autosteer
description: Run the full development pipeline (plan, implement, validate, review, branch, commit, PR, YouTrack update) autonomously without pausing for user confirmation between phases. Use when you want hands-off task completion. Stops only on errors.
argument-hint: "[ticket-id-or-task-description]"
---

# Autosteer

Run the full development pipeline end-to-end without pausing for user
confirmation between phases. The agent proceeds autonomously through every
stage, stopping **only** when a phase fails (tests, lint, coverage).

## Activation

When this skill is invoked, the **pacing rule** from `CLAUDE.md` is
suspended for the remainder of the current task. Concretely:

- Do **not** pause between phases to ask for confirmation.
- Do **not** present a plan and wait for a go-ahead — just execute.
- Do **not** pause before pushing or creating the PR.
- **Do** stop immediately if a quality gate fails (`make check`,
  `make test`, `make test-cov-check`) and attempt to fix it. If you
  cannot fix it after two attempts, stop and report the failure.

## Steps

### 1. Resolve the ticket

If the argument looks like a ticket ID (`DBA-XXX`, a bare number, or a
YouTrack URL), fetch it with `get_issue` and move it to **Develop**.

If the argument is a free-text task description without a ticket ID,
create a YouTrack issue automatically:

- Derive **Summary** (imperative, one-line) and **Description**
  (2-4 sentences) from the argument text.
- Type: infer Bug / Task / Feature; default to Task.
- Create via `create_issue` in the **DBA** project.
- Move to **Develop**.

If no argument is provided, ask the user once for a task description or
ticket ID, then proceed autonomously from that point.

### 2. Plan

Read the ticket (or task description) and relevant source files.
Outline the approach internally — do not present it to the user.
Proceed immediately to implementation.

### 3. Implement

Write the code changes and tests. Run `make test` to verify.
If tests fail, fix and re-run (up to two retries).

### 4. Validate

Run quality gates sequentially:

1. `make check` — auto-fix ruff issues if needed, re-run.
2. `make test-cov-check` — if coverage is below threshold, write
   additional tests and re-run.

If a gate still fails after two fix attempts, stop and report.

### 5. Review

Run `local-code-review` and `review-architecture` skills **in parallel**
(both use `context: fork`). Inspect findings:

- **Critical / High severity** — fix them, then re-run validate (step 4).
- **Medium / Low** — note them but proceed.

### 6. Branch and commit

- Use the `create-branch` skill to create a feature branch.
- Stage specific files and commit following **Commit Messages** in
  `CLAUDE.md`.

### 7. PR

- Push with `-u` flag.
- Create the PR via `gh pr create` using the template from the
  `create-pr` skill. Skip the pre-push confirmation pause.

### 8. Update YouTrack

- Move the ticket to **Review** state.
- Add a comment with the PR URL and the Claude Code session cost
  (from `/cost`).

### 9. Report

Output a final summary:

- Ticket ID and link
- Branch name
- PR URL
- Any review findings that were not auto-fixed

## Guardrails

- Never commit or push to `main` — always branch first.
- Never skip quality gates — they are blocking even in autosteer mode.
- Never create a YouTrack issue without at least a task description
  (from argument or one user prompt).
- If `gh` CLI or YouTrack MCP is unavailable, stop and inform the user.
- Stage specific files — never use `git add -A` or `git add .`.
