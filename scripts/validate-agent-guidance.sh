#!/usr/bin/env bash
set -euo pipefail

# Tier 1: Static validation of agent skills and guidance docs.
# Checks structural correctness, cross-references, and parity between
# Claude Code skills and Cursor rules.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$ROOT_DIR/.claude/skills"
CURSOR_DIR="$ROOT_DIR/.cursor/rules"
SHARED_FILE="$ROOT_DIR/docs/agent-shared.md"
MAKEFILE="$ROOT_DIR/Makefile"

errors=0

error() {
  echo "ERROR: $1" >&2
  errors=$((errors + 1))
}

warn() {
  echo "WARN: $1" >&2
}

# ---------- 1. SKILL.md structure ----------

for skill_dir in "$SKILLS_DIR"/*/; do
  skill_name="$(basename "$skill_dir")"
  skill_file="$skill_dir/SKILL.md"

  if [[ ! -f "$skill_file" ]]; then
    error "Skill '$skill_name' has no SKILL.md"
    continue
  fi

  # Check required sections
  if ! grep -q '^# ' "$skill_file"; then
    error "$skill_name/SKILL.md missing top-level heading (# Title)"
  fi
  if ! grep -q '^## When to use' "$skill_file"; then
    error "$skill_name/SKILL.md missing '## When to use' section"
  fi
  # Require actionable content: Steps section, numbered subsections, or checklist sections
  if ! grep -qE '^## Steps|^### [0-9]|^## .+ checklist' "$skill_file"; then
    error "$skill_name/SKILL.md missing '## Steps', numbered step sections, or checklist sections"
  fi
done

# ---------- 2. Cursor parity ----------

# Every Claude skill should have a matching Cursor rule
for skill_dir in "$SKILLS_DIR"/*/; do
  skill_name="$(basename "$skill_dir")"
  cursor_file="$CURSOR_DIR/${skill_name}.mdc"
  if [[ ! -f "$cursor_file" ]]; then
    error "Claude skill '$skill_name' has no matching Cursor rule at .cursor/rules/${skill_name}.mdc"
  fi
done

# Every Cursor rule should have a matching Claude skill
for cursor_file in "$CURSOR_DIR"/*.mdc; do
  rule_name="$(basename "$cursor_file" .mdc)"
  skill_dir="$SKILLS_DIR/$rule_name"
  if [[ ! -d "$skill_dir" ]]; then
    error "Cursor rule '$rule_name' has no matching Claude skill at .claude/skills/${rule_name}/"
  fi
done

# ---------- 3. Make target existence ----------

# Extract make targets referenced in skills and docs
check_make_target() {
  local target="$1"
  local source="$2"
  if ! grep -qE "^${target}:" "$MAKEFILE" 2>/dev/null; then
    error "Make target '$target' referenced in $source does not exist in Makefile"
  fi
}

# Check skills for make targets
for skill_file in "$SKILLS_DIR"/*/SKILL.md; do
  skill_name="$(basename "$(dirname "$skill_file")")"
  # Match patterns like `make setup`, `make check`, `make test-cov-check`
  while IFS= read -r target; do
    check_make_target "$target" "$skill_name/SKILL.md"
  done < <(grep -oE '`make ([a-z][a-z0-9_-]*)`' "$skill_file" | sed 's/`make \(.*\)`/\1/' | sort -u)
done

# Check agent-shared.md for make targets
if [[ -f "$SHARED_FILE" ]]; then
  while IFS= read -r target; do
    check_make_target "$target" "docs/agent-shared.md"
  done < <(grep -oE '`make ([a-z][a-z0-9_-]*)`' "$SHARED_FILE" | sed 's/`make \(.*\)`/\1/' | sort -u)
fi

# ---------- 4. Script existence ----------

for skill_file in "$SKILLS_DIR"/*/SKILL.md; do
  skill_name="$(basename "$(dirname "$skill_file")")"
  while IFS= read -r script; do
    script_path="$ROOT_DIR/$script"
    if [[ ! -f "$script_path" ]]; then
      error "Script '$script' referenced in $skill_name/SKILL.md does not exist"
    elif [[ ! -x "$script_path" ]]; then
      error "Script '$script' referenced in $skill_name/SKILL.md is not executable"
    fi
  done < <(grep -oE 'scripts/[a-z][a-z0-9_-]*\.sh' "$skill_file" | sort -u)
done

# ---------- 5. Cross-doc consistency ----------

# Check that docs referenced in agent-shared.md exist
if [[ -f "$SHARED_FILE" ]]; then
  while IFS= read -r doc; do
    doc_path="$ROOT_DIR/$doc"
    if [[ ! -f "$doc_path" ]]; then
      error "Doc '$doc' referenced in docs/agent-shared.md does not exist"
    fi
  done < <(grep -oE '`docs/[a-z][a-z0-9_/-]*\.(md|txt)`' "$SHARED_FILE" | tr -d '`' | sort -u)
fi

# Check Shared References in CLAUDE.md
claude_file="$ROOT_DIR/CLAUDE.md"
if [[ -f "$claude_file" ]]; then
  while IFS= read -r doc; do
    doc_path="$ROOT_DIR/$doc"
    if [[ ! -f "$doc_path" ]]; then
      error "Doc '$doc' referenced in CLAUDE.md does not exist"
    fi
  done < <(grep -oE '`docs/[a-z][a-z0-9_/-]*\.(md|txt)`' "$claude_file" | tr -d '`' | sort -u)
fi

# ---------- 6. Eval files validation ----------

# Skills exempt from requiring evals (meta-skills that evaluate other skills)
EVAL_EXEMPT_SKILLS="eval-skills"

for skill_dir in "$SKILLS_DIR"/*/; do
  skill_name="$(basename "$skill_dir")"
  eval_file="$skill_dir/evals/evals.json"

  if [[ -f "$eval_file" ]]; then
    # Validate JSON syntax
    if ! python3 -c "import json; json.load(open('$eval_file'))" 2>/dev/null; then
      error "$skill_name/evals/evals.json is not valid JSON"
    fi
  else
    # Require evals for non-exempt skills
    if [[ ! " $EVAL_EXEMPT_SKILLS " =~ " $skill_name " ]]; then
      error "Skill '$skill_name' is missing evals/evals.json — add eval test cases"
    fi
  fi
done

# ---------- Summary ----------

if [[ $errors -gt 0 ]]; then
  echo ""
  echo "Agent guidance validation failed with $errors error(s)." >&2
  exit 1
fi

echo "Agent guidance validation passed."
