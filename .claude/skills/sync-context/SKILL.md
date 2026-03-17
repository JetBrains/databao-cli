# Sync Agent Context

Regenerate agent entrypoint files (`CLAUDE.md`, `.cursorrules`) from the
single source of truth in `docs/agent-shared.md`.

## When to use

- Mid-session, after editing `docs/agent-shared.md` or the delta headers in
  `scripts/sync-agent-context.sh`, so that subsequent work sees fresh context.
- Note: commit-time sync is handled automatically by a pre-commit hook — you
  only need this skill for mid-session updates.

## Steps

```bash
scripts/sync-agent-context.sh
```

Verify with `git diff --stat` — expect changes in `CLAUDE.md` and `.cursorrules`.

## Failure handling

- "Missing shared core" → ensure `docs/agent-shared.md` exists and is not empty.
- Divergent output → compare `docs/agent-shared.md` against the "Shared Core"
  sections in the generated files.
