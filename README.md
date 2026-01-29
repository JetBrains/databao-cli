# Databao CLI

A command-line interface tool for managing Databao Agents and Context Engine (DCE) components.

## Requirements

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/)

## Installation

To set up the project locally, clone the repository and install the dependencies:

```bash
uv sync
```

## Usage

Once installed, you can use the `databao` command.

### General Help

```bash
databao --help
```

### Agents Commands

To interact with agents:

```bash
databao agents hello
# Example output: "Hello from Agents!"
```

### DCE Commands

To interact with DCE:

```bash
databao dce hello
# Example output: "Hello from DCE!"
```

## Development

### Setup

Install development dependencies:

```bash
uv sync
```

### Running Tests

This project uses pytest for testing:

```bash
uv run pytest
```

### Linting

Run flake8 to check code style:

```bash
uv run flake8 src tests
```