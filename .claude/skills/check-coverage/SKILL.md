---
name: check-coverage
description: Run test coverage measurement, analyze results, and fix gaps when coverage falls below the 80% threshold.
---

# Check Coverage

## Steps

### 1. Run `make test-cov-check`

If tests pass and coverage >= 80%, done.

### 2. If tests fail

- **Existing tests broke**: fix production code, not tests.
- **New tests fail**: fix the test.
- **Ambiguous**: read test intent. If behavior intentionally changed, update
  test and document in commit message.

### 3. If coverage below 80%

Check "Missing" column. Prioritize:
1. New code you just wrote (must have tests).
2. Critical paths (error handling, validation, CLI logic).
3. Utility functions with clear contracts.

Do NOT: add trivial tests just to raise numbers, add `# pragma: no cover`
without justification, or test third-party/Streamlit internals.

### 4. Write tests

Add to `tests/test_<module>.py`. Use `project_layout` fixture when needed.
One behavior per test function.

### 5. Re-run `make test-cov-check`

Repeat until threshold met.

### 6. HTML report (optional)

`make test-cov` -- opens `htmlcov/index.html`.

## Failure handling

- Missing `pytest-cov`: run `uv sync --dev`.
- Uncoverable lines (platform-specific, external calls): add
  `# pragma: no cover` with reason, note in commit message.
