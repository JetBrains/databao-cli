# Sync Agent Context

Regenerate agent entrypoint files (`CLAUDE.md`, `.cursorrules`) from the single
source of truth in `docs/agent-shared.md`.

## When to use

- After editing `docs/agent-shared.md` (shared project context).
- After editing the agent-specific delta headers in `scripts/sync-agent-context.sh`.
- Before committing changes that touch agent configuration to ensure all
  entrypoints are consistent.
- When onboarding a new coding agent and want to verify the sync pipeline works.

## Steps

### 1. Run the sync script

```bash
scripts/sync-agent-context.sh
```

This regenerates two files from `docs/agent-shared.md`:

| Generated file   | Consumer   |
|------------------|------------|
| `CLAUDE.md`      | Claude Code |
| `.cursorrules`   | Cursor     |

Each file gets an agent-specific header (delta) prepended before the shared core.

### 2. Verify the output

```bash
# Confirm all three files were updated
git diff --stat

# Spot-check that the shared core section matches
grep -c "Shared Core" CLAUDE.md .cursorrules
# Expected: each file reports 1 match
```

### 3. Review diffs

Skim the generated diffs to confirm:

- The shared core section in each file is identical.
- Agent-specific delta headers are preserved and correct.
- No unintended content was dropped or duplicated.

### 4. Stage and commit

If everything looks good, stage the regenerated files:

```bash
git add CLAUDE.md .cursorrules
```

## Failure handling

- If the script exits with "Missing shared core", ensure `docs/agent-shared.md`
  exists and is not empty.
- If generated files diverge unexpectedly, compare `docs/agent-shared.md` against
  the "Shared Core" section in each output file.

## What this skill does NOT do

- It does not edit `docs/agent-shared.md` — make content changes there first,
  then run this skill to propagate them.
- It does not sync Cursor rule files (`.cursor/rules/*.mdc`) — those are
  maintained separately.
- It does not create or modify `docs/architecture.md`, `docs/coding-guidelines.md`,
  or `docs/testing-strategy.md`.
