# Databao Demo — Streamlit in Snowflake

This project deploys the [Databao](https://github.com/JetBrains/databao-cli) Streamlit UI as a native **Streamlit-in-Snowflake (SiS)** application. It connects to a Snowflake database as its datasource using OAuth (the Streamlit app's own session), loads secrets at runtime via a Snowflake UDF, and runs the chat-based data exploration interface directly inside your Snowflake account.

## Prerequisites

- A Snowflake account with privileges to create databases, warehouses, integrations, and Streamlit apps
- An OpenAI API key and/or an Anthropic API key
- A Snowflake warehouse and database with data you want the Databao agent to explore

## How It Works

1. **`setup.sql`** provisions everything needed inside Snowflake:
   - A dedicated database and warehouse (named with a configurable suffix)
   - Network rules and external access integrations for outbound HTTPS
   - A Git repository object pointing at `databao-cli` on GitHub
   - Snowflake secrets for the OpenAI/Anthropic API keys and datasource coordinates (warehouse, database)
   - A Python UDF (`get_secret`) that reads those secrets at runtime
   - The Streamlit app itself, running on `SYSTEM_COMPUTE_POOL_CPU` (or an optional dedicated compute pool)

2. **`cleanup.sql`** removes all objects created by `setup.sql` for a given suffix.

3. **`app.py`** is the Streamlit entry point that adapts `databao-cli`'s UI for Snowflake:
   - Detects whether it is running inside Snowflake (via `/snowflake/session/token`)
   - Calls `get_secret()` through a Snowflake SQL session to load secrets into environment variables (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `SNOWFLAKE_DS_*`)
   - Locates and configures the ADBC Snowflake driver shared library so DuckDB's Snowflake extension can find it
   - Launches the standard Databao UI in **read-only domain** mode

4. **`databao/domains/root/`** contains the Databao domain definition -- a Snowflake datasource configured via environment variables and sample context files that ship with the demo.

## Setup

### 1. Configure `setup.sql`

Open `setup.sql` and fill in the placeholder values at the top:

| Variable | Description |
|---|---|
| `suffix` | Name suffix appended to all Snowflake objects. Set to e.g. `V2` to create a fully independent copy (objects will be named `STREAMLIT_DATABAO_DB_V2`, etc.). Changing the suffix lets you run multiple independent instances side by side. |
| `openai_api_key` | OpenAI API key |
| `anthropic_key` | Anthropic API key |
| `snowflake_ds_warehouse` | Warehouse the Databao agent will use to run queries against the datasource |
| `snowflake_ds_database` | Database containing the data the agent will explore |

The datasource connection uses the Streamlit app's own OAuth session -- no separate service user or password is needed. The user running the Streamlit app must have access to the target warehouse and database.

### 2. Run the Setup Script

Execute the entire `setup.sql` in a Snowflake worksheet (or via SnowSQL). The script is idempotent -- it uses `CREATE OR REPLACE` throughout, so re-running it is safe.

### 3. Open the App

Once the script finishes, navigate to **Streamlit** in Snowsight and open the app (named `STREAMLIT_DATABAO_APP_<suffix>`, e.g. `STREAMLIT_DATABAO_APP_DEMO`). The system compute pool may take a minute or two to resume on first launch.

## Cleanup

To remove all Snowflake objects created by `setup.sql`, open `cleanup.sql`, set the same `suffix` you used during setup, and run the script. This drops the database (cascading to all database-scoped objects), integrations, and warehouse.

## Local Development

```bash
# From the examples/demo-snowflake-project directory
uv sync

# Set the required environment variables
export OPENAI_API_KEY="..."
export ANTHROPIC_API_KEY="..."
export SNOWFLAKE_DS_WAREHOUSE="..."
export SNOWFLAKE_DS_DATABASE="..."

# Run the Streamlit app
uv run streamlit run src/databao_snowflake_demo/app.py -- \
  --project-dir .
```

When running locally, the Snowflake secret-loading logic is skipped (it only activates inside a Snowflake container). Environment variables must be set manually.

## Updating the `databao` Package

This project has its own `uv.lock` and installs `databao` from PyPI (not from the workspace). To update to a newer release:

```bash
# From the examples/demo-snowflake-project directory
uv lock -P databao
```

To test a dev/pre-release version, update the version specifier in `pyproject.toml` to include the pre-release tag (e.g. `databao>=0.4.0.dev1`), then re-lock. Pre-release specifiers tell `uv` to allow pre-releases for that package.

## Notes

- The app runs in **read-only domain** mode — datasource configuration and domain builds are disabled in the UI. All domain setup is done ahead of time via the files in `databao/domains/root/`.
- The app uses `SYSTEM_COMPUTE_POOL_CPU` by default. To use a dedicated compute pool, uncomment the relevant section in `setup.sql`.
- Network egress is allowed on ports 80 and 443 to enable OpenAI/Anthropic API calls and Snowflake datasource connections.
