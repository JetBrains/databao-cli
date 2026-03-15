from dataclasses import dataclass
from pathlib import Path

import duckdb


@dataclass(frozen=True)
class DuckdbDB:
    datasource_name: str | None = "test duckdb conn"
    datasource_type: str = "duckdb"
    database_path: Path | None = None
    check_connection: bool = False
    check_connection_succeed: bool = True

    @classmethod
    def get_database(cls, db_file: Path):
        return cls(database_path=db_file, check_connection=True)

    def add_table(self, create_table_sql: str, fill_table_sql: str):
        conn = duckdb.connect(database=str(self.database_path))
        try:
            with conn:
                conn.execute(create_table_sql)
                conn.execute(fill_table_sql)
        finally:
            conn.close()


CREATE_DUCKDB_TABLE_SQL = """
                           CREATE TABLE all_types_demo
                           (
                               -- Integer types
                               id                INTEGER PRIMARY KEY,
                               tinyint_col       TINYINT,
                               smallint_col      SMALLINT,
                               int_col           INTEGER,
                               bigint_col        BIGINT,
                               hugeint_col       HUGEINT,

                               -- Unsigned integers
                               utinyint_col      UTINYINT,
                               usmallint_col     USMALLINT,
                               uinteger_col      UINTEGER,
                               ubigint_col       UBIGINT,

                               -- Floating point
                               real_col          REAL,
                               double_col DOUBLE,

                               -- Decimal
                               decimal_col       DECIMAL(10, 2),

                               -- Boolean
                               boolean_col       BOOLEAN,

                               -- Character / string
                               char_col          CHAR(5),
                               varchar_col       VARCHAR,
                               text_col          TEXT,

                               -- Binary
                               blob_col          BLOB,

                               -- Date & time
                               date_col          DATE,
                               time_col          TIME,
                               timestamp_col     TIMESTAMP,
                               timestamptz_col   TIMESTAMPTZ,
                               interval_col INTERVAL,

                               -- UUID
                               uuid_col          UUID,

                               -- JSON
                               json_col          JSON,

                               -- Arrays (LIST)
                               int_array_col     INTEGER[],
                               varchar_array_col VARCHAR[],

                               -- Struct
                               struct_col        STRUCT(name VARCHAR, age INTEGER),

                               -- Map
                               map_col           MAP(VARCHAR, INTEGER)
                           );"""

FILL_DUCKDB_TABLE_SQL = """
                         INSERT INTO all_types_demo
                         VALUES (1,
                                 10,
                                 100,
                                 1000,
                                 10000000000,
                                 123456789012345678901234567890::HUGEINT,
                                 255,
                                 65535,
                                 4000000000,
                                 10000000000000000000,
                                 3.14,
                                 3.1415926535,
                                 12345.67,
                                 TRUE,
                                 'ABCDE',
                                 'Hello DuckDB',
                                 'This is a text column',
                                 'DEADBEEF'::BLOB,
                                 DATE '2025-01-01',
                                 TIME '12:30:00',
                                 TIMESTAMP '2025-01-01 12:30:00',
                                 TIMESTAMPTZ '2025-01-01 12:30:00+02',
                                 INTERVAL '2 days',
                                 '550e8400-e29b-41d4-a716-446655440000'::UUID,
                                 '{"key": "value"}'::JSON,
                                    [1, 2, 3],
                                    ['a', 'b', 'c'],
                                    {'name' : 'Alice', 'age': 30},
                                 MAP(['a', 'b'], [1, 2]));"""
