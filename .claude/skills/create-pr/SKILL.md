---
name: create-pr
description: Stage, commit, push, and open a GitHub PR following project conventions. Use when code is ready to ship.
compatibility: gh must be installed and authenticated.
---

# Create PR

## Steps

### 1. Verify preconditions

- Must NOT be on `main`. If so, run `create-branch` skill first.
- Check `git status` for changes. If clean, inform user and stop.

### 2. Run quality gates

Run all three gates from **Quality Gates** in `CLAUDE.md`. Do not commit
until they pass.

### 3. Stage and commit

- Extract ticket ID from branch name (`DBA-<number>`) or ask user.
- Stage specific files (never `git add -A`).
- Commit per **Commit Messages** in `CLAUDE.md`.

### 4. Pause for confirmation

Show branch, commit(s), and draft PR description. Wait for explicit approval.

> **Autosteer exception**: skip this pause.

### 5. Push and create PR

Push with `-u` flag. Create PR via `gh pr create` using this template:

```
## Summary
<1-3 sentence overview>

## Changes

### <Logical change 1>
<Brief description>
<details><summary>Files</summary>

- `path/to/file`
</details>

## Test Plan
- [ ] <Verification step>
```

### 6. Report

Output the PR URL.

## Guardrails

- Never push to `main`.
- Never push without user confirmation (except autosteer).
- Never skip commit prefix when ticket is known.
- Never use `git add -A` or `git add .`.
- If `gh` unavailable, show manual push/PR instructions.
