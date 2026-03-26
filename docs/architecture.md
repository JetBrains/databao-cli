# Architecture

## Overview
Databao CLI is a Python CLI application built with Click that provides a
command-line and web interface to the Databao Agent and Context Engine.

Project structure:
```
src/databao_cli/
- commands/           # CLI routing layer (Click wrappers only)
- workflows/          # Interactive CLI sequences (REPL, wizards, result display)
- features/           # Business logic, organized by feature — no Click dependency
- shared/             # Cross-feature utilities and models
```

## Key Dependencies
- `databao-context-engine` — core context indexing and querying
- `databao-agent` — AI agent for natural language interaction
- `click` — CLI framework
- `streamlit` — web UI framework
- `fastmcp` — MCP server framework

## Entry Point
`databao_cli.__main__:cli` — a Click group that registers all subcommands and
is exposed as the `databao` console script (run as `databao ...` after installation).
During development, it can also be invoked via `uv run databao`.

## Layer Responsibilities

### `commands/` — Routing Layer
Contains only Click wiring: decorators, option/argument definitions, and calls
to workflow or feature functions. No business logic lives here.

- Single command = single file; file name MUST match the command name.
- Grouped commands MUST be organized in subdirectories (e.g. `commands/datasource/`).
- All commands and groups MUST be registered in `src/databao_cli/__main__.py`
  via the `COMMANDS` collection.

### `workflows/` — Interactive CLI Layer
Interactive CLI sequences that need multi-step user interaction (prompts,
confirmations, REPL loops) or result display. Uses Click freely. Calls into
`features/` for business operations. Complex workflows get a subdirectory;
thin workflows are a single file.

```
workflows/
  ask.py              # run_interactive_mode, run_one_shot_mode, display_result
  datasource/
    add.py            # add_workflow (interactive wizard: prompts, confirms, echoes)
    check.py          # print_connection_check_results
```

Commands that require no interaction (build, index, status) skip this layer and
call `features/` directly.

### `features/` — Business Logic Layer
All application logic lives here, organized by feature. No Click dependency —
`features/` functions are pure business operations callable from any context
(CLI, MCP, tests). Complex features get a subdirectory; thin features are a
single file.

```
features/
  ask/
    agent_factory.py  # initialize_agent_from_dce — returns Agent
    display.py        # dataframe_to_prettytable (pure formatter, returns str)
    service.py        # ask_impl — validates args, initialises agent
  init/
    errors.py         # project initialization error types
    service.py        # init_impl, _ProjectCreator
  datasource/
    add.py            # datasource_config_exists, create_datasource_config
    check.py          # check_impl — returns connection results dict
  mcp/
    server.py         # FastMCP server setup, mcp_impl
    tools/            # individual MCP tool handlers
  ui/
    app.py            # main Streamlit entry point
    cli.py            # bootstrap_streamlit_app, app_impl
    pages/            # individual UI pages
    components/       # reusable UI components
    services/         # backend service wrappers
    models/           # data models for UI state
    streaming.py      # streaming writer for real-time output
    project_utils.py  # project status helpers used across features
    suggestions.py    # suggested questions logic
  build.py            # build_impl
  index.py            # index_impl
  status.py           # status_impl, info string generation
```

### `shared/` — Shared Utilities
Cross-feature code with no business logic of its own.

```
shared/
  project/
    layout.py         # ProjectLayout dataclass, find_project
  log/
    logging.py        # configure_logging
    llm_errors.py     # format_llm_error (user-friendly API error messages)
  cli_utils.py        # get_project_or_raise, handle_feature_errors
  context_engine_cli.py  # ClickUserInputCallback (Click ↔ DCE adapter)
  executor_utils.py   # build_llm_config, LLM provider/model constants
  errors.py           # FeatureError
```

## Extension Points
- Add CLI command: create module in `commands/`, then add it to the
  `COMMANDS` collection in `src/databao_cli/__main__.py`.
- Add interactive workflow: create module in `workflows/`, call from command.
- Add MCP tool: add handler in `features/mcp/tools/`, register in
  `features/mcp/server.py`.
- Add datasource type: extend via `databao-context-engine` optional deps.
- Add UI page: add to `features/ui/pages/`.
