#!/usr/bin/env bash
set -euo pipefail

# Tier 1: Static validation of agent skills and guidance docs.
# Checks structural correctness, cross-references, and file existence.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$ROOT_DIR/.claude/skills"
CLAUDE_FILE="$ROOT_DIR/CLAUDE.md"
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

# ---------- 2. Make target existence ----------

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

# Check CLAUDE.md for make targets
if [[ -f "$CLAUDE_FILE" ]]; then
  while IFS= read -r target; do
    check_make_target "$target" "CLAUDE.md"
  done < <(grep -oE '`make ([a-z][a-z0-9_-]*)`' "$CLAUDE_FILE" | sed 's/`make \(.*\)`/\1/' | sort -u)
fi

# ---------- 3. Script existence ----------

for skill_file in "$SKILLS_DIR"/*/SKILL.md; do
  skill_name="$(basename "$(dirname "$skill_file")")"
  while IFS= read -r script; do
    script_path="$ROOT_DIR/$script"
    if [[ ! -f "$script_path" ]]; then
      error "Script '$script' referenced in $skill_name/SKILL.md does not exist"
    elif [[ ! -x "$script_path" ]]; then
      error "Script '$script' referenced in $skill_name/SKILL.md is not executable"
    fi
  done < <(grep -v '\${' "$skill_file" | grep -oE 'scripts/[a-z][a-z0-9_.-]*\.sh' | sort -u)
done

# ---------- 4. Cross-doc consistency ----------

# Check that docs referenced in CLAUDE.md exist
if [[ -f "$CLAUDE_FILE" ]]; then
  while IFS= read -r doc; do
    doc_path="$ROOT_DIR/$doc"
    if [[ ! -f "$doc_path" ]]; then
      error "Doc '$doc' referenced in CLAUDE.md does not exist"
    fi
  done < <(grep -oE '`docs/[a-z][a-z0-9_/-]*\.(md|txt)`' "$CLAUDE_FILE" | tr -d '`' | sort -u)
fi

# ---------- 5. Eval files validation ----------

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
