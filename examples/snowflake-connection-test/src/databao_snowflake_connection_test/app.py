"""Minimal Streamlit app to test Snowflake connectivity.

Uses the same auth strategies as demo-snowflake-project:
- Local dev: externalbrowser (interactive OAuth)
- Streamlit-in-Snowflake (SiS): OAuth session token from /snowflake/session/token

Required environment variables:
  SNOWFLAKE_ACCOUNT       - Snowflake account identifier (e.g. myorg-myaccount)
  SNOWFLAKE_DS_WAREHOUSE  - Warehouse to use
  SNOWFLAKE_DS_DATABASE   - Database to connect to

Optional (set automatically in SiS/SPCS):
  SNOWFLAKE_HOST          - Required when using OAuth session token
"""

import os
from pathlib import Path

import snowflake.connector
import streamlit as st

SESSION_TOKEN_PATH = Path("/snowflake/session/token")


def _is_running_in_snowflake() -> bool:
    return SESSION_TOKEN_PATH.exists()


def _get_sis_token() -> str:
    return SESSION_TOKEN_PATH.read_text().strip()


def _test_connection(
    account: str,
    warehouse: str | None,
    database: str | None,
) -> str:
    """Connect to Snowflake, run SELECT 1, return a status message."""
    connect_kwargs: dict[str, object] = {
        "account": account,
        "warehouse": warehouse,
        "database": database,
    }

    if _is_running_in_snowflake():
        connect_kwargs["authenticator"] = "oauth"
        connect_kwargs["token"] = _get_sis_token()
        if host := os.environ.get("SNOWFLAKE_HOST"):
            connect_kwargs["host"] = host
    else:
        connect_kwargs["authenticator"] = "externalbrowser"

    snowflake.connector.paramstyle = "qmark"
    conn = snowflake.connector.connect(**connect_kwargs)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        if result is None or result[0] != 1:
            return f"Unexpected result: {result}"
        return f"SELECT 1 returned: {result[0]}"
    finally:
        conn.close()


def main() -> None:
    st.title("Snowflake Connection Test")

    account = os.environ.get("SNOWFLAKE_ACCOUNT", "")
    warehouse = os.environ.get("SNOWFLAKE_DS_WAREHOUSE", "")
    database = os.environ.get("SNOWFLAKE_DS_DATABASE", "")
    auth_mode = "OAuth session token (SiS)" if _is_running_in_snowflake() else "externalbrowser"

    st.markdown("**Connection parameters** (from environment variables)")
    st.table({
        "Parameter": ["Account", "Warehouse", "Database", "Auth"],
        "Value": [account or "—", warehouse or "—", database or "—", auth_mode],
    })

    if not account:
        st.warning("Set `SNOWFLAKE_ACCOUNT` to enable the connection test.")
        return

    if st.button("Test Connection"):
        with st.spinner("Connecting..."):
            try:
                message = _test_connection(account, warehouse or None, database or None)
                st.success(f"Connection successful. {message}")
            except Exception as exc:
                st.error(f"Connection failed: {exc}")


main()
