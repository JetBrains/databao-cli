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

import importlib.util
import logging
import os
from pathlib import Path

import databao.agent as bao
import duckdb
import snowflake
import streamlit as st
from databao_context_engine import SnowflakeConnectionProperties, SnowflakeOAuthAuth
from databao.agent.executors.separate.separate_executor import SeparateExecutor
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

SESSION_TOKEN_PATH = Path("/snowflake/session/token")
ADBC_LIB = "libadbc_driver_snowflake.so"

SNOWFLAKE_SECRETS: dict[str, str] = {
    "openai_api_key": "OPENAI_API_KEY",
}


def _is_running_in_snowflake() -> bool:
    return SESSION_TOKEN_PATH.exists()


def _get_sis_token() -> str:
    return SESSION_TOKEN_PATH.read_text().strip()


def _get_snowflake_host() -> str | None:
    return os.environ.get("SNOWFLAKE_HOST")


def _ensure_adbc_driver() -> None:
    """Point the DuckDB Snowflake extension at the ADBC driver .so.

    The extension checks SNOWFLAKE_ADBC_DRIVER_PATH before anything else.
    We set it to the absolute path of the .so inside the pip package, which
    avoids the dlopen-vs-stat cwd mismatch (stat finds bare filenames in
    cwd, but dlopen does not search cwd on Linux).
    """
    if os.environ.get("SNOWFLAKE_ADBC_DRIVER_PATH"):
        return

    spec = importlib.util.find_spec("adbc_driver_snowflake")
    if not spec or not spec.origin:
        logger.error(
            "adbc_driver_snowflake package not installed, skipping driver setup"
        )
        return

    so_file = Path(spec.origin).parent / ADBC_LIB
    if not so_file.exists():
        logger.error("ADBC .so not found at %s", so_file)
        return

    abs_path = str(so_file.resolve())
    os.environ["SNOWFLAKE_ADBC_DRIVER_PATH"] = abs_path
    print(f"[ADBC] Set SNOWFLAKE_ADBC_DRIVER_PATH={abs_path}")

def _load_snowflake_secrets() -> None:
    conn = st.connection("snowflake")
    session = conn.session()

    for secret_name, env_var in SNOWFLAKE_SECRETS.items():
        if os.environ.get(env_var):
            continue
        try:
            row = session.sql(f"SELECT get_secret('{secret_name}')").collect()
            value = row[0][0] if row else None
            if value:
                os.environ[env_var] = value
                logger.info("Loaded Snowflake secret '%s' -> %s", secret_name, env_var)
            else:
                logger.warning("Snowflake secret '%s' returned empty", secret_name)
        except Exception:
            logger.warning("Failed to load secret '%s'", secret_name, exc_info=True)

def _get_account_identifier() -> str:
    conn = st.connection("snowflake")
    session = conn.session()

    return session.sql("""
    SELECT CURRENT_ORGANIZATION_NAME() || '-' || CURRENT_ACCOUNT_NAME()
    """).collect()[0][0]

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
        if host := _get_snowflake_host():
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

    # domain = bao.domain()
    # domain.add_db(db = SnowflakeConnectionProperties(
    #     account = account,
    #     warehouse = warehouse,
    #     database = database,
    #     auth=SnowflakeOAuthAuth(token=_get_sis_token()),
    # ))
    #
    # agent = bao.agent(domain=domain, name="my_agent", llm_config=bao.LLMConfig(name="gpt-5.1", temperature=0))
    #
    # agent.thread().ask("How many accidents occurred in total?")


def _test_connection_sqlalchemy(
    account: str,
    warehouse: str | None,
    database: str | None,
) -> str:
    """Connect to Snowflake via SQLAlchemy, run SELECT 1, return a status message."""
    connect_args: dict[str, object] = {}

    if _is_running_in_snowflake():
        connect_args["authenticator"] = "oauth"
        connect_args["token"] = _get_sis_token()
        if host := _get_snowflake_host():
            connect_args["host"] = host
    else:
        connect_args["authenticator"] = "externalbrowser"

    url = URL(
        account=account,
        warehouse=warehouse,
        database=database,
    )
    engine = create_engine(url, connect_args=connect_args)
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).fetchone()
        if result is None or result[0] != 1:
            return f"Unexpected result: {result}"
        return f"SELECT 1 returned: {result[0]}"
    finally:
        engine.dispose()


def _test_connection_databao(
    account: str,
    warehouse: str | None,
    database: str | None,
) -> str:
    host = _get_snowflake_host()

    domain = bao.domain()
    domain.add_db(db = SnowflakeConnectionProperties(
        account = account,
        warehouse = warehouse,
        database = database,
        auth=SnowflakeOAuthAuth(token=_get_sis_token()),
        additional_properties={"host": host}
    ))

    agent = bao.agent(
        domain=domain,
        data_executor=SeparateExecutor(),
        name="my_agent",
        llm_config=bao.LLMConfig(name="gpt-5.1", temperature=0),
    )

    agent.thread().ask("Where does Philip Wennblom live?")




_ensure_adbc_driver()

def main() -> None:
    st.title("Snowflake Connection Test")

    if _is_running_in_snowflake():
        _load_snowflake_secrets()

    # account = os.environ.get("SNOWFLAKE_ACCOUNT", "")
    account = _get_account_identifier()
    warehouse = os.environ.get("SNOWFLAKE_DS_WAREHOUSE", "SNOWFLAKE_LEARNING_WH")
    database = os.environ.get("SNOWFLAKE_DS_DATABASE", "DATAGRIP")
    auth_mode = "OAuth session token (SiS)" if _is_running_in_snowflake() else "externalbrowser"
    token = _get_sis_token() if _is_running_in_snowflake() else None
    host = _get_snowflake_host() if _is_running_in_snowflake() else None

    st.markdown("**Connection parameters** (from environment variables)")
    st.table({
        "Parameter": ["Account", "Warehouse", "Database", "Host", "Auth", "Token"],
        "Value": [account or "—", warehouse or "—", database or "—", host or "—", auth_mode, token or "—"],
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

    if st.button("Test Connection (SQLAlchemy)"):
        with st.spinner("Connecting via SQLAlchemy..."):
            try:
                message = _test_connection_sqlalchemy(account, warehouse or None, database or None)
                st.success(f"SQLAlchemy connection successful. {message}")
            except Exception as exc:
                st.error(f"SQLAlchemy connection failed: {exc}")

    if st.button("Test Connection (Databao)"):
        with st.spinner("Connecting via Databao..."):
            try:
                message = _test_connection_databao(account, warehouse or None, database or None)
                st.success(f"Databao connection successful. {message}")
            except Exception as exc:
                st.error(f"Databao connection failed: {exc}")

    # --- DuckDB Chat ---
    st.divider()
    st.subheader("DuckDB Chat")

    if "duckdb_conn" not in st.session_state:
        st.session_state.duckdb_conn = duckdb.connect()

    if "duckdb_messages" not in st.session_state:
        st.session_state.duckdb_messages: list[dict[str, object]] = []

    for msg in st.session_state.duckdb_messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.code(msg["content"], language="sql")
            else:
                if isinstance(msg["content"], str):
                    st.markdown(msg["content"])
                else:
                    st.dataframe(msg["content"])

    if query := st.chat_input("Enter a SQL query for DuckDB"):
        st.session_state.duckdb_messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.code(query, language="sql")

        with st.chat_message("assistant"):
            try:
                result = st.session_state.duckdb_conn.sql(query)
                df = result.fetchdf()
                st.dataframe(df)
                st.session_state.duckdb_messages.append(
                    {"role": "assistant", "content": df}
                )
            except Exception as exc:
                error_msg = f"Error: {exc}"
                st.error(error_msg)
                st.session_state.duckdb_messages.append(
                    {"role": "assistant", "content": error_msg}
                )


main()
