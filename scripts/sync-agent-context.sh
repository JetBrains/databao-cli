#!/usr/bin/env bash
set -euo pipefail

# Sync AGENTS.md and CLAUDE.md from docs/agent-shared.md.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SHARED_FILE="$ROOT_DIR/docs/agent-shared.md"
AGENTS_FILE="$ROOT_DIR/AGENTS.md"
CLAUDE_FILE="$ROOT_DIR/CLAUDE.md"

if [[ ! -f "$SHARED_FILE" ]]; then
  echo "Missing shared core: $SHARED_FILE" >&2
  exit 1
fi

{
  cat <<'EOF'
# AGENTS.md

OpenCode entrypoint for agent instructions in this repository.

## Agent Delta (OpenCode)

- Default to concise, implementation-first responses.
- Prefer direct execution over back-and-forth planning unless blocked.

## Shared References

- `docs/architecture.md`
- `docs/coding-guidelines.md`
- `docs/testing-strategy.md`
- `docs/agent-shared.md`

## Sync

- This file should stay aligned with `CLAUDE.md`.
- Canonical shared content lives in `docs/agent-shared.md`.
- Regenerate both files with `scripts/sync-agent-context.sh`.

## Shared Core (synced from `docs/agent-shared.md`)

EOF
  cat "$SHARED_FILE"
} >"$AGENTS_FILE"

{
  cat <<'EOF'
# CLAUDE.md

Claude Code entrypoint for agent instructions in this repository.

## Agent Delta (Claude Code)

- Prefer concise updates with clear file/command references.
- Execute directly when safe; ask questions only if truly blocked.

## Shared References

- `docs/architecture.md`
- `docs/coding-guidelines.md`
- `docs/testing-strategy.md`
- `docs/agent-shared.md`

## Sync

- This file should stay aligned with `AGENTS.md`.
- Canonical shared content lives in `docs/agent-shared.md`.
- Regenerate both files with `scripts/sync-agent-context.sh`.

## Shared Core (synced from `docs/agent-shared.md`)

EOF
  cat "$SHARED_FILE"
} >"$CLAUDE_FILE"

echo "Synced: AGENTS.md and CLAUDE.md"
