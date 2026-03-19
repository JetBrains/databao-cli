---
name: create-branch
description: Create a feature branch following project naming conventions. Use when starting work on a ticket, after understanding the scope, or when the agent needs to branch off main for new work.
---

# Create Branch

Create a feature branch following the `<nickname>/<descriptive-branch-name>`
convention used in this repository.

## Steps

### 1. Detect the user's nickname

Query existing remote branches to find the most frequent author prefix:

```bash
git branch -r | sed -nE 's|^ *origin/([^/]+)/.*|\1|p' | grep -vE '^(dependabot|HEAD|revert-)' | sort | uniq -c | sort -rn
```

Pick the top result. If ambiguous or no branches exist, ask the user.

### 2. Derive a descriptive branch name

Combine the ticket ID (if available) and a short slug describing the change:

- Use lowercase kebab-case: `fix-auth-timeout`, `add-mcp-tool-list`
- Keep it under 50 characters
- If a YouTrack ticket is known (e.g., `DBA-123`), prefer including it:
  `<nickname>/DBA-123-fix-auth-timeout`

### 3. Ensure a clean starting point

- Fetch latest: `git fetch origin`
- If the working tree has uncommitted changes, warn the user and ask whether
  to stash or proceed.
- Branch from `main` (or the base branch the user specifies):
  `git checkout -b <nickname>/<branch-name> origin/main`

### 4. Confirm

Report the created branch name to the user.

## Guardrails

- Never create branches directly on `main` — always branch _from_ main.
- Never silently discard uncommitted changes.
- If the user is already on a feature branch, ask before switching.
