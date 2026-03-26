---
name: check-coverage
description: Run test coverage measurement, analyze results, and fix gaps when coverage falls below the 80% threshold. Use after implementing features or fixing bugs, when `make test-cov-check` fails, when reviewing module test adequacy, or before creating a PR that touches `src/databao_cli/`.
---

# Check Coverage

Run test coverage measurement, analyze results, and fix gaps when coverage
falls below the 80% threshold.

## Steps

### 1. Run coverage measurement

```bash
make test-cov-check
```

If all tests pass and coverage is ≥80%, you are done. Otherwise continue.

### 2. If tests fail (non-zero exit from pytest itself)

Before looking at coverage, fix the test failures:

- **Existing tests broke after your code change**: The production code is
  likely wrong. Fix the code in `src/databao_cli/`, not the tests. The
  existing tests encode expected behavior — do not weaken them to make
  them pass.
- **Newly written tests fail**: The test itself has a bug. Fix the test.
- **Ambiguous case**: Read the test name and docstring to understand its
  intent. If the test asserts correct prior behavior that your change
  intentionally alters, update the test and document the behavioral change
  in the commit message.

### 3. If coverage is below 80%

Examine the "Missing" column in the terminal report to identify uncovered
lines. Prioritize:

1. New code you just wrote — this should always have tests.
2. Critical paths (error handling, validation, CLI command logic).
3. Utility functions with clear input/output contracts.

Do NOT:
- Add empty or trivial tests solely to raise the coverage number.
- Add `# pragma: no cover` to bypass the threshold without justification.
- Test third-party library behavior or Streamlit UI internals.

### 4. Write targeted tests

Add tests in the corresponding `tests/test_<module>.py` file. Follow the
existing pattern:
- Use `project_layout` fixture from `conftest.py` when the test needs a
  project directory.
- One behavior per test function.
- Test file mirrors source module structure.

### 5. Re-run and verify

```bash
make test-cov-check
```

Repeat steps 2–5 until the threshold is met and all tests pass.

### 6. Generate HTML report (optional)

```bash
make test-cov
```

Open `htmlcov/index.html` to visually inspect coverage.

## Failure handling

- If `pytest-cov` is not installed, run `uv sync --dev` first.
- If coverage is below 80% and you cannot reasonably cover the uncovered
  lines (e.g., platform-specific code, external service calls), add a
  brief `# pragma: no cover` comment with a reason, and note it in the
  commit message.

## What this skill does NOT do

- It does not run e2e tests or measure their coverage.
- It does not modify the 80% threshold — that is set in `pyproject.toml`.
- It does not auto-generate tests — it guides you to write meaningful ones.
