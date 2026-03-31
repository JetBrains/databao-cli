---
name: update-pr
description: Stage, commit, and push follow-up changes to an existing feature branch or PR. Use for quick iterations.
compatibility: gh must be installed and authenticated.
---

# Update PR

Stage, commit, and push to the current feature branch for fast iterations.

## Steps

### 1. Verify preconditions

- Must NOT be on `main`. If so, run `create-branch` skill first.
- Check `git status`. If clean, inform user and stop.

### 2. Run quality gates

Run gates from **Quality Gates** in `CLAUDE.md`. Do not commit until they pass.

### 3. Stage and commit

- Stage specific files (never `git add -A`).
- Extract ticket ID from branch name if it contains `DBA-<number>`.
- Commit per **Commit Messages** in `CLAUDE.md`.

### 4. Push

Push to tracked remote. If no upstream: `git push -u origin <branch>`.

### 5. Report

Confirm push, show commit hash. Show PR URL if one exists for the branch.

## Guardrails

- Never push to `main`.
- Never use `git add -A` or `git add .`.
- Never skip commit prefix when ticket is known.
