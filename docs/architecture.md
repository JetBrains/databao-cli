# Architecture

## Overview

Databao CLI is a Python CLI application built with Click that provides a
command-line and web interface to the Databao Agent and Context Engine.

Key layers:

- CLI commands (`src/databao_cli/commands/`)
- Web UI via Streamlit (`src/databao_cli/ui/`)
- MCP server (`src/databao_cli/mcp/`)
- Project management (`src/databao_cli/project/`)
- Logging (`src/databao_cli/log/`)

## Entry Point

`databao_cli.__main__:cli` — a Click group that registers all subcommands.

## CLI Commands

| Command              | Module                          | Purpose                         |
|----------------------|---------------------------------|---------------------------------|
| `databao init`       | `commands/init.py`              | Initialize a new project        |
| `databao status`     | `commands/status.py`            | Show project status             |
| `databao datasource` | `commands/datasource/`          | Add/check data sources          |
| `databao build`      | `commands/build.py`             | Build context for datasources   |
| `databao ask`        | `commands/ask.py`               | Interactive chat with agent     |
| `databao app`        | `commands/app.py`               | Launch Streamlit web UI         |
| `databao mcp`        | `commands/mcp.py`               | Run MCP server                  |

## Web UI (Streamlit)

`src/databao_cli/ui/` contains the Streamlit application:

- `app.py` — main Streamlit entry
- `pages/` — individual UI pages
- `components/` — reusable UI components
- `services/` — backend service wrappers
- `models/` — data models for UI state

## MCP Server

`src/databao_cli/mcp/` exposes tools via the Model Context Protocol:

- `server.py` — FastMCP server setup
- `tools/` — individual tool handlers

## Key Dependencies

- `databao-context-engine` — core context indexing and querying
- `databao-agent` — AI agent for natural language interaction
- `click` — CLI framework
- `streamlit` — web UI framework
- `fastmcp` — MCP server framework

## Database Support

Multi-database via optional dependencies: Snowflake (default), BigQuery,
ClickHouse, Athena, MS SQL, with ADBC drivers.

## Extension Points

- Add CLI command: create module in `commands/`, register with Click group
  in `__main__.py`.
- Add MCP tool: add handler in `mcp/tools/`, register in `mcp/server.py`.
- Add datasource type: extend via `databao-context-engine` optional deps.
- Add UI page: add to `ui/pages/`.
