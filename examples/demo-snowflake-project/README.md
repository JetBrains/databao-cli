# Databao Demo — Streamlit in Snowflake

This project deploys the [Databao](https://github.com/JetBrains/databao-cli) Streamlit UI as a native **Streamlit-in-Snowflake (SiS)** application. It connects to a Snowflake database as its datasource, loads secrets at runtime via a Snowflake UDF, and runs the chat-based data exploration interface directly inside your Snowflake account.

## Prerequisites

- A Snowflake account with `ACCOUNTADMIN` privileges (for the initial setup)
- An OpenAI API key and/or an Anthropic API key
- A Snowflake database with data you want the Databao agent to explore (see [Datasource credentials](#datasource-credentials-sf_ds_) below)

## How It Works

1. **`setup.sql`** provisions everything needed inside Snowflake:
   - A dedicated database, warehouse, and compute pool (all named with a configurable suffix)
   - Network rules and external access integrations for outbound HTTPS
   - A service user with a permissive network policy
   - A Git repository object pointing at `databao-cli` on GitHub
   - Snowflake secrets for the OpenAI/Anthropic API keys and datasource credentials
   - A Python UDF (`get_secret`) that reads those secrets at runtime
   - The Streamlit app itself, running on a container runtime (`CPU_X64_M`)

2. **`cleanup.sql`** removes all objects created by `setup.sql` for a given suffix.

3. **`app.py`** is the Streamlit entry point that adapts `databao-cli`'s UI for Snowflake:
   - Detects whether it is running inside Snowflake (via `/snowflake/session/token`)
   - Calls `get_secret()` through a Snowflake SQL session to load secrets into environment variables (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `SNOWFLAKE_DS_*`)
   - Locates and configures the ADBC Snowflake driver shared library so DuckDB's Snowflake extension can find it
   - Launches the standard Databao UI in **read-only domain** mode

4. **`databao/domains/root/`** contains the Databao domain definition — a Snowflake datasource configured via environment variables and sample context files that ship with the demo.

## Setup

### 1. Configure `setup.sql`

Open `setup.sql` and fill in the placeholder values at the top:

| Variable | Description |
|---|---|
| `suffix` | Name suffix appended to all Snowflake objects. Set to e.g. `V2` to create a fully independent copy (objects will be named `STREAMLIT_DATABAO_DB_V2`, etc.). Changing the suffix lets you run multiple independent instances side by side. |
| `openai_key` | OpenAI API key |
| `anthropic_key` | Anthropic API key |
| `sf_ds_account` | Snowflake datasource account identifier (see [below](#datasource-credentials-sf_ds_)) |
| `sf_ds_warehouse` | Warehouse for the datasource (see [below](#datasource-credentials-sf_ds_)) |
| `sf_ds_database` | Database to explore (see [below](#datasource-credentials-sf_ds_)) |
| `sf_ds_user` | Service user for the datasource (see [below](#datasource-credentials-sf_ds_)) |
| `sf_ds_password` | Password for that service user |

#### Datasource credentials (`sf_ds_*`)

These credentials are used by the Databao agent to connect to a Snowflake database via the Snowflake API. The agent reads data from this database to answer your questions.

- **`sf_ds_account`** — your Snowflake account identifier (e.g. `abc12345.us-east-1`). You can find it in Snowsight under your account menu.

- **`sf_ds_warehouse`** — the warehouse the agent will use to run queries. If you don't have one, create it in **Snowsight → Admin → Warehouses → + Warehouse** (an `XSMALL` warehouse is sufficient).

- **`sf_ds_database`** — the database containing the data the agent will explore.

- **`sf_ds_user`** and **`sf_ds_password`** — a service user that the agent authenticates as. To create one:
  1. Go to **Snowsight → Admin → Users & Roles → + User**
  2. Enter a name (e.g. `STREAMLIT_SERVICE_USER`)
  3. Set a password
  4. Click **Create User**
  5. Grant the user access to the target database and warehouse:

```sql
GRANT USAGE ON WAREHOUSE <your_warehouse> TO USER <your_service_user>;
GRANT USAGE ON DATABASE <your_database> TO USER <your_service_user>;
GRANT USAGE ON ALL SCHEMAS IN DATABASE <your_database> TO USER <your_service_user>;
GRANT SELECT ON ALL TABLES IN DATABASE <your_database> TO USER <your_service_user>;
```

### 2. Run the Setup Script

Execute the entire `setup.sql` in a Snowflake worksheet (or via SnowSQL) while connected as `ACCOUNTADMIN`. The script is idempotent — it uses `CREATE OR REPLACE` throughout, so re-running it is safe.

### 3. Open the App

Once the script finishes, navigate to **Streamlit** in Snowsight and open the app (named `STREAMLIT_DATABAO_APP_<suffix>`, e.g. `STREAMLIT_DATABAO_APP_DEMO`). The compute pool may take a minute or two to resume on first launch.

## Cleanup

To remove all Snowflake objects created by `setup.sql`, open `cleanup.sql`, set the same `suffix` you used during setup, and run the script as `ACCOUNTADMIN`. This drops the database (cascading to all database-scoped objects), compute pool, integrations, service user, network policy, and warehouse.

## Local Development

```bash
# From the examples/demo-snowflake-project directory
uv sync

# Set the required environment variables
export OPENAI_API_KEY="..."
export ANTHROPIC_API_KEY="..."
export SNOWFLAKE_DS_ACCOUNT="..."
export SNOWFLAKE_DS_WAREHOUSE="..."
export SNOWFLAKE_DS_DATABASE="..."
export SNOWFLAKE_DS_USER="..."
export SNOWFLAKE_DS_PASSWORD="..."

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
- The compute pool uses `CPU_X64_M` instances with auto-suspend after 5 minutes and auto-resume enabled.
- Network egress is allowed on ports 80 and 443 to enable OpenAI/Anthropic API calls and Snowflake datasource connections.
