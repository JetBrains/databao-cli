import importlib.util
import logging
import os
import sys
from pathlib import Path

import streamlit as st

from databao_cli.ui.app import main

logger = logging.getLogger(__name__)

SNOWFLAKE_SECRETS: dict[str, str] = {
    "openai_api_key": "OPENAI_API_KEY",
    "snowflake_ds_account": "SNOWFLAKE_DS_ACCOUNT",
    "snowflake_ds_warehouse": "SNOWFLAKE_DS_WAREHOUSE",
    "snowflake_ds_database": "SNOWFLAKE_DS_DATABASE",
    "snowflake_ds_user": "SNOWFLAKE_DS_USER",
    "snowflake_ds_password": "SNOWFLAKE_DS_PASSWORD",
}

ADBC_LIB = "libadbc_driver_snowflake.so"


def _is_running_in_snowflake() -> bool:
    return Path("/snowflake/session/token").exists()


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
        logger.warning("adbc_driver_snowflake package not installed, skipping driver setup")
        return

    so_file = Path(spec.origin).parent / ADBC_LIB
    if not so_file.exists():
        logger.warning("ADBC .so not found at %s", so_file)
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


if _is_running_in_snowflake():
    _ensure_adbc_driver()
    _load_snowflake_secrets()

if "--read-only-domain" not in sys.argv:
    sys.argv.append("--read-only-domain")

main()
