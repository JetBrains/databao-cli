---
name: sync-context
description: Regenerate CLAUDE.md from docs/agent-shared.md. Use mid-session after editing shared guidance.
---

# Sync Agent Context

Regenerate `CLAUDE.md` from the single source of truth in `docs/agent-shared.md`.
(`.cursor/rules/project-context.mdc` uses `@file` references and does not need syncing.)

## When to use

- Mid-session, after editing `docs/agent-shared.md` or the delta headers in
  the sync script, so that subsequent work sees fresh context.
- Note: commit-time sync is handled automatically by a pre-commit hook — you
  only need this skill for mid-session updates.

## Steps

```bash
${CLAUDE_SKILL_DIR}/scripts/sync.sh
```

Verify with `git diff --stat` — expect changes in `CLAUDE.md`.

## Failure handling

- "Missing shared core" → ensure `docs/agent-shared.md` exists and is not empty.
- Divergent output → compare `docs/agent-shared.md` against the "Shared Core"
  sections in the generated files.
