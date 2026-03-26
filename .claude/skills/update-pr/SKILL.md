---
name: update-pr
description: Stage, commit, and push follow-up changes to an existing feature branch or PR. Use for quick iterations — after addressing review feedback, fixing a bug on the branch, or adding incremental changes that don't need a new PR.
compatibility: gh must be installed and authenticated.
---

# Update PR

Stage changes, commit, and push to the current feature branch. Designed for
fast iterations on an existing branch or open PR.

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

### 3. Stage and commit

- Stage relevant files (prefer explicit paths over `git add -A`).
- Extract the ticket ID from the branch name if it contains `DBA-<number>`.
- Commit following the **Commit Messages** section in `CLAUDE.md`.

### 4. Push

- Push to the tracked remote branch: `git push`.
- If no upstream is set, push with `-u`: `git push -u origin <branch>`.

### 5. Report

Confirm the push succeeded and show the commit hash. If a PR exists for
the branch, show the PR URL.

## Guardrails

- Never push to `main`.
- Never use `git add -A` or `git add .` — stage specific files.
- Never skip the commit prefix when a ticket is known (see `CLAUDE.md`).
