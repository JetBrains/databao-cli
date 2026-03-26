---
name: write-tests
description: Write or update unit tests for changed code, following project conventions and ensuring coverage meets the 80% threshold. Use after implementing a feature, command, or MCP tool, after fixing a bug (regression test), when asked to cover existing code, or when `make test-cov-check` reports missing coverage.
---

# Write Tests

Write or update unit tests for new or changed code in `src/databao_cli/`,
following project conventions and ensuring the coverage threshold is met.

## Steps

### 1. Identify what to test

Read the source module(s) you need to cover. Focus on:

- Public functions and CLI command handlers.
- Branches: error paths, edge cases, validation logic.
- New or changed behavior — not unchanged code.

Do NOT test:

- Third-party library internals or Streamlit UI (`src/databao_cli/ui/`).
- Trivial pass-through wrappers with no logic.

### 2. Locate or create the test file

Test files live in `tests/` and mirror source modules:

| Source module                          | Test file                      |
|----------------------------------------|--------------------------------|
| `src/databao_cli/commands/init.py`     | `tests/test_init.py`          |
| `src/databao_cli/commands/build.py`    | `tests/test_build.py`         |
| `src/databao_cli/mcp/tools/<name>.py`  | `tests/test_mcp.py`           |
| `src/databao_cli/commands/datasource/add.py` | `tests/test_add_datasource.py` |

If the test file already exists, add tests to it. Create a new file only when
no matching test file exists.

### 3. Follow project test conventions

- **Framework**: `pytest` — no `unittest.TestCase` subclasses.
- **Fixtures**: use the `project_layout` fixture from `conftest.py` when the
  test needs an initialized project directory. Use `tmp_path` for isolated
  filesystem operations.
- **CLI testing**: use `click.testing.CliRunner` to invoke CLI commands. Import
  the top-level `cli` group from `databao_cli.__main__`. Check `result.exit_code`
  and `result.output` / `result.stderr`.
- **One behavior per test**: each test function asserts one logical behavior.
  Name it `test_<action>_<scenario>` (e.g., `test_init_fails_when_project_exists`).
- **Type hints**: add return type `-> None` to all test functions.
- **Mocking**: mock external I/O (network, subprocess, Docker) but do NOT mock
  internal project modules — test real behavior. Use `unittest.mock.patch` or
  `pytest.monkeypatch`.
- **Helpers**: if you need shared test utilities, place them in `tests/utils/`.

### 4. Write the tests

For each behavior to cover:

1. **Arrange** — set up inputs, fixtures, and any mocks.
2. **Act** — call the function or invoke the CLI command.
3. **Assert** — verify the expected outcome (return value, side effects, output,
   exit code, raised exception).

Keep assertions specific and actionable. Prefer checking exact values over
truthiness. Include error message context in assertions:

```python
assert result.exit_code == 0, f"Expected success but got: {result.output}"
```

### 5. Run and verify

```bash
uv run pytest tests/test_<module>.py -v
```

Fix any failures. Then run the full suite with coverage:

```bash
make test-cov-check
```

If coverage is still below 80%, identify remaining uncovered lines from the
report and add more tests. Repeat until the threshold is met.

### 6. Lint and type-check

```bash
make check
```

Fix any ruff or mypy errors in the new test code before considering the
tests complete.

## What this skill does NOT do

- It does not write e2e tests (those use `pexpect` and `testcontainers`).
- It does not modify the coverage threshold — that is set in `pyproject.toml`.
- It does not weaken existing tests to make them pass. If existing tests break
  after a code change, fix the production code first (see `check-coverage` skill).
