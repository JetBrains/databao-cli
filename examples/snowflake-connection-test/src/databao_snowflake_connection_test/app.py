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
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import snowflake.connector
import streamlit as st
from databao.agent.databases.snowflake_adapter import SnowflakeAdapter
from databao_context_engine.plugins.databases.snowflake.snowflake_introspector import (
    SnowflakeIntrospector,
)

logger = logging.getLogger(__name__)

SESSION_TOKEN_PATH = Path("/snowflake/session/token")
ADBC_LIB = "libadbc_driver_snowflake.so"


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


def _patch_snowflake_introspector_for_sis() -> None:
    """Monkey-patch SnowflakeIntrospector._connect for Streamlit-in-Snowflake (SiS).

    In SiS, the SPCS runtime maintains an OAuth session token at
    ``/snowflake/session/token``.  We re-read it on every connection to handle
    token refresh (tokens are valid ~1 hour, the file refreshes every few
    minutes).
    """

    @contextmanager
    def _sis_connect(
        self: Any, file_config: Any, *, catalog: str | None = None
    ) -> Any:
        snowflake.connector.paramstyle = "qmark"
        kwargs = file_config.connection.to_snowflake_kwargs()
        for key in (
            "password",
            "private_key",
            "private_key_file",
            "private_key_file_pwd",
        ):
            kwargs.pop(key, None)
        kwargs["authenticator"] = "oauth"
        kwargs["token"] = _get_sis_token()
        if host := _get_snowflake_host():
            kwargs["host"] = host
        if catalog:
            kwargs["database"] = catalog
        conn = snowflake.connector.connect(**kwargs)
        try:
            yield conn
        finally:
            conn.close()

    SnowflakeIntrospector._connect = _sis_connect  # type: ignore[assignment]
    logger.info("Patched SnowflakeIntrospector._connect for SiS OAuth token auth")


def _patch_snowflake_adapter_for_sis() -> None:
    """Monkey-patch SnowflakeAdapter for SiS OAuth token auth."""
    original_create_connection_string = SnowflakeAdapter._create_connection_string

    @staticmethod  # type: ignore[misc]
    def _sis_create_secret_sql(config: Any, name: str) -> str:
        params = {
            "account": config.account,
            "auth_type": "oauth",
            "token": _get_sis_token(),
        }
        if config.user:
            params["user"] = config.user
        if config.database:
            params["database"] = config.database
        if config.warehouse:
            params["warehouse"] = config.warehouse
        if config.role:
            params["role"] = config.role
        if host := _get_snowflake_host():
            params["host"] = host

        def _escape(v: str) -> str:
            return v.replace("'", "''")

        kv = ", ".join(f"{k} '{_escape(v)}'" for k, v in params.items())
        return f'CREATE OR REPLACE SECRET "{name}" (TYPE snowflake, {kv});'

    @staticmethod  # type: ignore[misc]
    def _sis_create_connection_string(config: Any) -> str:
        original = original_create_connection_string(config)
        parts = dict(part.split("=", 1) for part in original.split(";") if "=" in part)
        for key in ("auth_type", "password", "private_key", "private_key_passphrase"):
            parts.pop(key, None)
        if host := _get_snowflake_host():
            parts["host"] = host
        parts["auth_type"] = "oauth"
        parts["token"] = _get_sis_token()
        return ";".join(f"{k}={v}" for k, v in parts.items() if v is not None)

    SnowflakeAdapter._create_secret_sql = _sis_create_secret_sql  # type: ignore[assignment]
    SnowflakeAdapter._create_connection_string = _sis_create_connection_string  # type: ignore[assignment]
    logger.info("Patched SnowflakeAdapter for SiS OAuth token auth")


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


_ensure_adbc_driver()
if _is_running_in_snowflake():
    _patch_snowflake_introspector_for_sis()
    _patch_snowflake_adapter_for_sis()


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
