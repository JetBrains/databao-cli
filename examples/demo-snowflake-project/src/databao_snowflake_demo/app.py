import importlib.util
import logging
import os
import sys
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import snowflake.connector
import streamlit as st
from databao_context_engine.plugins.databases.snowflake.snowflake_introspector import (
    SnowflakeIntrospector,
)

from databao_cli.ui.app import main

logger = logging.getLogger(__name__)

SNOWFLAKE_SECRETS: dict[str, str] = {
    "openai_api_key": "OPENAI_API_KEY",
    "anthropic_api_key": "ANTHROPIC_API_KEY",
    "snowflake_ds_warehouse": "SNOWFLAKE_DS_WAREHOUSE",
    "snowflake_ds_database": "SNOWFLAKE_DS_DATABASE",
}

SESSION_TOKEN_PATH = Path("/snowflake/session/token")

ADBC_LIB = "libadbc_driver_snowflake.so"


def _is_running_in_snowflake() -> bool:
    return SESSION_TOKEN_PATH.exists()


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
        logger.error("adbc_driver_snowflake package not installed, skipping driver setup")
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


def _patch_snowflake_introspector_for_sis() -> None:
    """Monkey-patch SnowflakeIntrospector._connect for Streamlit-in-Snowflake (SiS).

    In SiS, the runtime maintains an OAuth session token at
    /snowflake/session/token. We re-read it on every connection to avoid expiry
    (tokens are valid ~1 hour, the file refreshes every few minutes).

    DCE's _connect must return a context manager because BaseIntrospector uses
    ``with self._connect(file_config) as conn:``.
    """
    @contextmanager
    def _sis_connect(self: Any, file_config: Any, *, catalog: str | None = None) -> Generator[Any, None, None]:
        token = SESSION_TOKEN_PATH.read_text().strip()
        snowflake.connector.paramstyle = "qmark"
        kwargs = file_config.connection.to_snowflake_kwargs()
        # Replace any existing auth params with OAuth token
        kwargs.pop("password", None)
        kwargs.pop("private_key", None)
        kwargs.pop("private_key_file", None)
        kwargs.pop("private_key_file_pwd", None)
        kwargs.pop("authenticator", None)
        kwargs.pop("token", None)
        kwargs["authenticator"] = "oauth"
        kwargs["token"] = token
        if catalog:
            kwargs["database"] = catalog
        conn = snowflake.connector.connect(**kwargs)
        try:
            yield conn
        finally:
            conn.close()

    SnowflakeIntrospector._connect = _sis_connect  # type: ignore[assignment]
    logger.info("Patched SnowflakeIntrospector._connect for SiS OAuth token auth")


_ensure_adbc_driver()
if _is_running_in_snowflake():
    _load_snowflake_secrets()
    _patch_snowflake_introspector_for_sis()

if "--project-dir" not in sys.argv:
    sys.argv.extend(["--project-dir", "examples/demo-snowflake-project"])

if "--read-only-domain" not in sys.argv:
    sys.argv.append("--read-only-domain")
if "--hide-suggested-questions" not in sys.argv:
    sys.argv.append("--hide-suggested-questions")
if "--hide-build-context-hint" not in sys.argv:
    sys.argv.append("--hide-build-context-hint")

main()
