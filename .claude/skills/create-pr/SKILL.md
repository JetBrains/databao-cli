---
name: create-pr
description: Stage, commit, push, and open a GitHub PR following project conventions. Use when code is ready to ship — after tests pass, code review, and architecture review are done.
compatibility: gh must be installed and authenticated.
---

# Create PR

Stage changes, commit, push, and open a GitHub pull request following
project conventions.

## Steps

### 1. Verify preconditions

- Confirm you are NOT on `main`. If on `main`, run the `create-branch`
  skill to create a feature branch before continuing.
- Check `git status` for changes to commit. If nothing to commit, inform
  the user and stop.
### 2. Run quality gates

These are **blocking** — do not commit until both pass.

1. **`make check`** (ruff + mypy)
   - Run `make check`.
   - If ruff fails, auto-fix with `uv run ruff check --fix src/databao_cli && uv run ruff format src/databao_cli`, then re-run `make check`.
   - If mypy fails after ruff is clean, stop and fix the type errors before continuing.
2. **`make test`** (pytest)
   - Run `make test`.
   - If tests fail, stop and fix the failures before continuing.
3. **`make test-cov-check`** (coverage threshold)
   - Run `make test-cov-check`.
   - Warn the user if coverage is below threshold, but do **not** block the PR.

### 3. Determine the ticket ID

- Extract from the current branch name if it contains `DBA-<number>`.
- Otherwise ask the user for the ticket ID.

### 4. Stage and commit

- Stage relevant files (prefer explicit paths over `git add -A`).
- Commit following the **Commit Messages** section in `CLAUDE.md`.

### 5. Pause for confirmation

Present the user with:

- The branch name and commit(s) that will be pushed.
- A draft PR description following the template below.

**Wait for explicit user confirmation before proceeding.**

### 6. Push and create PR

- Push with `-u` flag: `git push -u origin <branch>`
- Create the PR via `gh pr create` using the template:

```
## Summary
<1-3 sentence overview of why this change exists>

## Changes

### <Logical change 1>
<Brief description>
<details><summary>Files</summary>

- `path/to/file1`
- `path/to/file2`
</details>

### <Logical change 2>
...

## Test Plan
- [ ] <Step or check to verify correctness>
```

### 7. Report

Output the PR URL so the user can review it.

## Guardrails

- Never push to `main`.
- Never push without explicit user confirmation.
- Never skip the commit prefix when a ticket is known (see `CLAUDE.md`).
- Never use `git add -A` or `git add .` — stage specific files.
- If `gh` CLI is not available, show the push command and PR URL for
  manual creation.
