---
name: write-tests
description: Write or update unit tests for changed code, following project conventions and ensuring coverage meets the 80% threshold.
---

# Write Tests

## Steps

### 1. Identify what to test

Read the source module(s). Focus on:
- Public functions and CLI command handlers
- Branches: error paths, edge cases, validation
- New or changed behavior

Skip: third-party internals, Streamlit UI, trivial pass-throughs.

### 2. Locate or create test file

Tests in `tests/` mirror source modules:

| Source | Test file |
|---|---|
| `src/databao_cli/commands/init.py` | `tests/test_init.py` |
| `src/databao_cli/commands/build.py` | `tests/test_build.py` |
| `src/databao_cli/mcp/tools/<name>.py` | `tests/test_mcp.py` |
| `src/databao_cli/commands/datasource/add.py` | `tests/test_add_datasource.py` |

Add to existing file when possible.

### 3. Conventions

- `pytest` only, no `unittest.TestCase`.
- Use `project_layout` fixture for project dirs, `tmp_path` for filesystem.
- CLI: `click.testing.CliRunner`, import `cli` from `databao_cli.__main__`.
- One behavior per test: `test_<action>_<scenario>`.
- Return type `-> None` on all test functions.
- Mock external I/O, not internal modules.

### 4. Write tests (Arrange/Act/Assert)

Specific assertions over truthiness. Include context:
```python
assert result.exit_code == 0, f"Expected success but got: {result.output}"
```

### 5. Run and verify

```bash
uv run pytest tests/test_<module>.py -v
make test-cov-check
```

Repeat until 80% threshold met.

### 6. Lint

Run `make check`. Fix ruff/mypy errors in test code.
