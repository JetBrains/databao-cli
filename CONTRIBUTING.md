# Contributing

`databao-cli` is open-source software. 
We welcome and encourage everyone to contribute code, documentation, report issues, or ask any questions they may have.

## Requirements

- Python >= 3.11
- [uv](https://docs.astral.sh/uv/)

## Installation

1. Clone the repository:

   ```bash
   git clone git@github.com:JetBrains/databao-cli.git
   ```

1. Install development dependencies:

   ```bash
   uv sync
   ```

### Running tests

This project uses [pytest](https://docs.pytest.org/en/stable/) for testing:

```bash
uv run pytest
```

### Running E2E tests

E2E tests are located in a separate project under `e2e-tests/`.
To run E2E tests:

```bash
uv run pytest e2e-tests
```

### Linting

Run [ruff](https://docs.astral.sh/ruff/) to check and format code:

```bash
uv run ruff check src tests e2e-tests
uv run ruff format src tests e2e-tests
```
