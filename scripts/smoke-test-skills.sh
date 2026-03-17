#!/usr/bin/env bash
set -euo pipefail

# Tier 2: Functional smoke tests for agent skills.
# Verifies that the commands and scripts each skill relies on actually work.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

passed=0
failed=0

run_test() {
  local name="$1"
  local cmd="$2"
  echo -n "  $name ... "
  if eval "$cmd" >/dev/null 2>&1; then
    echo "OK"
    passed=$((passed + 1))
  else
    echo "FAIL"
    failed=$((failed + 1))
  fi
}

echo "=== Tier 1: Static validation ==="
run_test "validate-agent-guidance" "scripts/validate-agent-guidance.sh"

echo ""
echo "=== Tier 2: Functional smoke tests ==="

# sync-context: script runs and produces files with expected markers
run_test "sync-context: script exits 0" "scripts/sync-agent-context.sh"
run_test "sync-context: CLAUDE.md contains shared core" "grep -q 'Shared Core' CLAUDE.md"
run_test "sync-context: .cursorrules contains shared core" "grep -q 'Shared Core' .cursorrules"

# setup-environment: make setup succeeds (already verifies toolchain)
run_test "setup-environment: make setup" "make setup"

# check-coverage: make test-cov-check succeeds
run_test "check-coverage: make test-cov-check" "make test-cov-check"

# review-architecture: referenced doc files exist and are non-empty
for doc in docs/architecture.md docs/coding-guidelines.md docs/testing-strategy.md docs/agent-shared.md README.md; do
  run_test "review-architecture: $doc exists and non-empty" "test -s $doc"
done

echo ""
echo "=== Results ==="
total=$((passed + failed))
echo "Passed: $passed / $total"
if [[ $failed -gt 0 ]]; then
  echo "Failed: $failed" >&2
  exit 1
fi
echo "All smoke tests passed."
