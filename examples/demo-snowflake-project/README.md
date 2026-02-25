# Databao Demo — Streamlit in Snowflake

This project deploys the [Databao](https://github.com/JetBrains/databao-cli) Streamlit UI as a native **Streamlit-in-Snowflake (SiS)** application. It connects to a Snowflake database as its datasource, loads secrets at runtime via a Snowflake UDF, and runs the chat-based data exploration interface directly inside your Snowflake account.

## Prerequisites

- A Snowflake account with `ACCOUNTADMIN` privileges (for the initial setup)
- A GitHub personal access token (PAT) with read access to the `databao-cli` repository
- An OpenAI API key
- A second Snowflake account/user to serve as the **datasource** (the database you want to explore through Databao)

## How It Works

1. **`setup.sql`** provisions everything needed inside Snowflake:
   - A dedicated database (`STREAMLIT_DATABAO`), warehouse, and compute pool
   - Network rules and external access integrations for outbound HTTPS
   - A service user with a permissive network policy
   - A Git repository object pointing at `databao-cli` on GitHub
   - Snowflake secrets for the OpenAI API key and datasource credentials
   - A Python UDF (`get_secret`) that reads those secrets at runtime
   - The Streamlit app itself, running on a container runtime (`CPU_X64_M`)

2. **`app.py`** is the Streamlit entry point that adapts `databao-cli`'s UI for Snowflake:
   - Detects whether it is running inside Snowflake (via `/snowflake/session/token`)
   - Calls `get_secret()` through a Snowflake SQL session to load secrets into environment variables (`OPENAI_API_KEY`, `SNOWFLAKE_DS_*`)
   - Locates and configures the ADBC Snowflake driver shared library so DuckDB's Snowflake extension can find it
   - Launches the standard Databao UI in **read-only domain** mode

3. **`databao/domains/root/`** contains the Databao domain definition — a Snowflake datasource configured via environment variables and sample context files that ship with the demo.

## Setup

### 1. Configure `setup.sql`

Open `setup.sql` and fill in the placeholder values at the top:

| Variable | Description |
|---|---|
| `git_pat` | GitHub PAT with repo read access |
| `git_username` | GitHub username associated with the PAT |
| `openai_key` | OpenAI API key |
| `sf_ds_account` | Snowflake datasource account identifier |
| `sf_ds_warehouse` | Warehouse on the datasource account |
| `sf_ds_database` | Database to explore |
| `sf_ds_user` | User on the datasource account |
| `sf_ds_password` | Password for that user |

### 2. Run the Setup Script

Execute the entire `setup.sql` in a Snowflake worksheet (or via SnowSQL) while connected as `ACCOUNTADMIN`. The script is idempotent — it uses `CREATE OR REPLACE` throughout, so re-running it is safe.

### 3. Open the App

Once the script finishes, navigate to **Streamlit** in Snowsight and open **STREAMLIT_DATABAO_DEMO_SNOWFLAKE**. The compute pool may take a minute or two to resume on first launch.

## Local Development

The project is part of the `databao-cli` uv workspace. To run it locally:

```bash
# From the databao-cli repository root
uv sync

# Set the required environment variables
export OPENAI_API_KEY="..."
export SNOWFLAKE_DS_ACCOUNT="..."
export SNOWFLAKE_DS_WAREHOUSE="..."
export SNOWFLAKE_DS_DATABASE="..."
export SNOWFLAKE_DS_USER="..."
export SNOWFLAKE_DS_PASSWORD="..."

# Run the Streamlit app
uv run streamlit run examples/demo-snowflake-project/src/databao_snowflake_demo/app.py -- \
  --project-dir examples/demo-snowflake-project
```

When running locally, the Snowflake secret-loading logic is skipped (it only activates inside a Snowflake container). Environment variables must be set manually.

## Notes

- The app runs in **read-only domain** mode — datasource configuration and domain builds are disabled in the UI. All domain setup is done ahead of time via the files in `databao/domains/root/`.
- The compute pool uses `CPU_X64_M` instances with auto-suspend after 5 minutes and auto-resume enabled.
- Network egress is allowed on ports 80 and 443 to enable OpenAI API calls and Snowflake datasource connections.
