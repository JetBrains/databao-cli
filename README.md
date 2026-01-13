# Databao CLI

This command-line interface tool is designed to manage Databao Agents and Context Engine (DCE) components.

## Installation

To set up the project locally, clone the repository and install the dependencies:

```bash
# Using poetry
poetry install
```
Or
``` bash
# Using pip
pip install .
```

## Usage
Once installed, you can use the databao command.

### General Help
``` bash
databao --help
```

### Agents Commands

To interact with agents:
``` bash
databao agents hello
# Example output: "Hello from Agents!"
```

### DCE Commands
To interact with DCE:
``` bash
databao dce hello
# Example output: "Hello from DCE!"
```

## Development
### Running Tests
This project uses pytest for testing. 

To run the tests, use:
``` bash
pytest
```