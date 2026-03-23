# Architecture

## Overview
Databao CLI is a Python CLI application built with Click that provides a
command-line and web interface to the Databao Agent and Context Engine.

Project structure:
```
src/databao_cli/
- commands/           # CLI commands
- ui/                 # Web UI (Streamlit)
- mcp/                # MCP server  
- project/            # Project management
- log/                # Logging
```

## Key Dependencies
- `databao-context-engine` — core context indexing and querying
- `databao-agent` — AI agent for natural language interaction
- `click` — CLI framework
- `streamlit` — web UI framework
- `fastmcp` — MCP server framework

## Entry Point
`databao_cli.__main__:cli` — a Click group that registers all subcommands.
Invoked as `uv run databao`.

## CLI Commands
The CLI is implemented using the Click framework.

### Structure
- All CLI commands are located in `src/databao_cli/commands/`
- Single command = single file.
- Each command MUST be implemented in its own module.
- File name SHOULD match the command name.
- Grouped commands MUST be organized in subdirectories. Example: `src/databao_cli/commands/datasource/`

### Registration
- All commands and groups MUST be explicitly registered in `src/databao_cli/__main__.py`
- Commands and groups are exposed via the COMMANDS collection. Every new command or group MUST be added to this collection to be discoverable by the CLI.

## Web UI (Streamlit)
```
src/databao_cli/ui/   # contains the Streamlit application
  app.py              # main Streamlit entry
  pages/              # individual UI pages
  components/         # reusable UI components
  services/           # backend service wrappers
  models/             # data models for UI state
```

## MCP Server
```
src/databao_cli/mcp/  # exposes tools via the Model Context Protocol:
  server.py           # FastMCP server setup
  tools/              # individual tool handlers
```

## Extension Points
- Add CLI command: create module in `commands/`, register with Click group
  in `__main__.py`.
- Add MCP tool: add handler in `mcp/tools/`, register in `mcp/server.py`.
- Add datasource type: extend via `databao-context-engine` optional deps.
- Add UI page: add to `ui/pages/`.
