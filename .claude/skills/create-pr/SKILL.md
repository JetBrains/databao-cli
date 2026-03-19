---
name: create-pr
description: Stage, commit, push, and open a GitHub PR following project conventions. Use when code is ready to ship — after tests pass, code review, and architecture review are done.
---

# Create PR

Stage changes, commit, push, and open a GitHub pull request following
project conventions.

## Steps

### 1. Verify preconditions

- Confirm you are NOT on `main`. Abort if so.
- Check `git status` for changes to commit. If nothing to commit, inform
  the user and stop.
- Warn (but do not block) if `make check` or `make test-cov-check` have
  not been run in this session.

### 2. Determine the ticket ID

- Extract from the current branch name if it contains `DBA-<number>`.
- Otherwise ask the user for the ticket ID.
- Prefix every commit message with the ticket ID: `[DBA-123] Description`.

### 3. Stage and commit

- Stage relevant files (prefer explicit paths over `git add -A`).
- Commit with `[DBA-XXX] Description of change`.

### 4. Pause for confirmation

Present the user with:

- The branch name and commit(s) that will be pushed.
- A draft PR description following the template below.

**Wait for explicit user confirmation before proceeding.**

### 5. Push and create PR

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

### 6. Report

Output the PR URL so the user can review it.

## Guardrails

- Never push to `main`.
- Never push without explicit user confirmation.
- Never skip the `[DBA-XXX]` commit prefix when a ticket is known.
- Never use `git add -A` or `git add .` — stage specific files.
- If `gh` CLI is not available, show the push command and PR URL for
  manual creation.
