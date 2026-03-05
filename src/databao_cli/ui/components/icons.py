"""Database icon and type detection utilities."""

from typing import Any

from databao.agent.databases import (
    DuckDBConnectionConfig,
    MySQLConnectionProperties,
    PostgresConnectionProperties,
    SnowflakeConnectionProperties,
    SQLiteConnectionConfig,
)

DB_ICONS = {
    "duckdb": "🦆",
    "postgres": "🐘",
    "postgresql": "🐘",
    "mysql": "🐬",
    "sqlite": "📦",
    "snowflake": "❄️",
    "default": "🗄️",
}

_CONFIG_TYPE_MAP: list[tuple[type, str, str]] = [
    (DuckDBConnectionConfig, "DuckDB", "duckdb"),
    (PostgresConnectionProperties, "PostgreSQL", "postgresql"),
    (MySQLConnectionProperties, "MySQL", "mysql"),
    (SQLiteConnectionConfig, "SQLite", "sqlite"),
    (SnowflakeConnectionProperties, "Snowflake", "snowflake"),
]


def get_db_icon(db_type: str) -> str:
    """Get icon for database type."""
    return DB_ICONS.get(db_type.lower(), DB_ICONS["default"])


def get_db_type_and_icon(conn: Any) -> tuple[str, str]:
    """Detect database type and icon from a connection object.

    Args:
        conn: A database connection (DBConnectionConfig, SQLAlchemy engine, DuckDB, etc.)

    Returns:
        Tuple of (db_type_display_name, icon_emoji).
    """
    for config_cls, display_name, icon_key in _CONFIG_TYPE_MAP:
        if isinstance(conn, config_cls):
            return display_name, get_db_icon(icon_key)

    if hasattr(conn, "dialect"):
        try:
            dialect = conn.dialect.name
            return dialect.capitalize(), get_db_icon(dialect)
        except Exception:
            return "Database", get_db_icon("default")

    if "duckdb" in type(conn).__name__.lower():
        return "DuckDB", get_db_icon("duckdb")

    return "Database", get_db_icon("default")
