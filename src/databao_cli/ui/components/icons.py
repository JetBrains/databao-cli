"""Database icon and type detection utilities."""

from typing import Any

from databao.databases import DBConnectionConfig

DB_ICONS = {
    "duckdb": "🦆",
    "postgres": "🐘",
    "postgresql": "🐘",
    "mysql": "🐬",
    "sqlite": "📦",
    "default": "🗄️",
}


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
    if isinstance(conn, DBConnectionConfig):
        db_type_str = conn.type.full_type
        return db_type_str.capitalize(), get_db_icon(db_type_str)

    if hasattr(conn, "dialect"):
        try:
            dialect = conn.dialect.name
            return dialect.capitalize(), get_db_icon(dialect)
        except Exception:
            return "Database", get_db_icon("default")

    if "duckdb" in type(conn).__name__.lower():
        return "DuckDB", get_db_icon("duckdb")

    return "Database", get_db_icon("default")
