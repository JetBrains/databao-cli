import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SqliteDB:
    datasource_name: str | None = "test sqlite conn"
    datasource_type: str = "sqlite"
    database_path: Path | None = None
    check_connection: bool = False
    check_connection_succeed: bool = True

    @classmethod
    def get_database(cls, db_file: Path):
        return cls(database_path=db_file, check_connection=True)

    def add_table(self, create_table_sql: str, fill_table_sql: str):
        conn = sqlite3.connect(database=str(self.database_path))
        try:
            with conn:
                conn.execute(create_table_sql)
                conn.execute(fill_table_sql)
        finally:
            conn.close()


CREATE_SQLITE_TABLE_SQL = """
                           CREATE TABLE all_types_demo
                           (
                               -- Primary key
                               id           INTEGER PRIMARY KEY AUTOINCREMENT,

                               -- INTEGER affinity
                               int_col      INTEGER,
                               bigint_col   BIGINT,
                               smallint_col SMALLINT,
                               tinyint_col  TINYINT,
                               boolean_col  BOOLEAN,

                               -- REAL affinity
                               real_col     REAL,
                               double_col DOUBLE,
                               float_col    FLOAT,
                               numeric_col  NUMERIC,
                               decimal_col  DECIMAL(10, 2),

                               -- TEXT affinity
                               char_col     CHAR(5),
                               varchar_col  VARCHAR(50),
                               text_col     TEXT,
                               clob_col     CLOB,
                               date_col     DATE,
                               datetime_col DATETIME,

                               -- BLOB affinity
                               blob_col     BLOB,

                               -- No type (NONE affinity)
                               no_type_col
                           );"""

FILL_SQLITE_TABLE_SQL = """
                         INSERT INTO all_types_demo (int_col,
                                                     bigint_col,
                                                     smallint_col,
                                                     tinyint_col,
                                                     boolean_col,
                                                     real_col,
                                                     double_col,
                                                     float_col,
                                                     numeric_col,
                                                     decimal_col,
                                                     char_col,
                                                     varchar_col,
                                                     text_col,
                                                     clob_col,
                                                     date_col,
                                                     datetime_col,
                                                     blob_col,
                                                     no_type_col)
                         VALUES (42,
                                 1234567890123,
                                 123,
                                 1,
                                 1, -- SQLite stores boolean as INTEGER
                                 3.14,
                                 3.1415926535,
                                 2.718,
                                 999.99,
                                 12345.67,
                                 'ABCDE',
                                 'Hello SQLite',
                                 'This is a text column',
                                 'This is a CLOB column',
                                 '2025-01-01',
                                 '2025-01-01 12:30:00',
                                 X'DEADBEEF', -- BLOB value
                                 'No declared type value');"""
