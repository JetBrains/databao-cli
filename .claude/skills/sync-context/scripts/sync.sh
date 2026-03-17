#!/usr/bin/env bash
set -euo pipefail

# Sync CLAUDE.md from docs/agent-shared.md.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && git rev-parse --show-toplevel)"
SHARED_FILE="$ROOT_DIR/docs/agent-shared.md"
CLAUDE_FILE="$ROOT_DIR/CLAUDE.md"

if [[ ! -f "$SHARED_FILE" ]]; then
  echo "Missing shared core: $SHARED_FILE" >&2
  exit 1
fi

{
  cat <<'EOF'
# CLAUDE.md

Claude Code entrypoint for agent instructions in this repository.

## Agent Delta (Claude Code)

- Prefer concise updates with clear file/command references.
- Execute directly when safe; ask questions only if truly blocked.
- YouTrack MCP must be configured (see DEVELOPMENT.md). Use get_issue / update_issue tools.

## Shared References

- `docs/architecture.md`
- `docs/coding-guidelines.md`
- `docs/testing-strategy.md`
- `docs/agent-shared.md`

## Sync

- Canonical shared content lives in `docs/agent-shared.md`.
- Regenerate with `.claude/skills/sync-context/scripts/sync.sh` or `/sync-context`.

## Shared Core (synced from `docs/agent-shared.md`)

EOF
  cat "$SHARED_FILE"
} >"$CLAUDE_FILE"

echo "Synced: CLAUDE.md"
