from dataclasses import dataclass

import psycopg2
from testcontainers.postgres import PostgresContainer


@dataclass(frozen=True)
class PostgresDB:
    datasource_name: str
    datasource_type = "postgres"
    host: str | None = None
    port: int | None = None
    database: str | None = None
    user: str | None = None
    password: str | None = None
    check_connection: bool = False
    check_connection_succeed: bool = True

    create_table_sql = """
                       CREATE TABLE all_types_demo
                       (
                           -- Numeric types
                           id              SERIAL PRIMARY KEY,
                           small_int_col   SMALLINT,
                           int_col         INTEGER,
                           big_int_col     BIGINT,
                           numeric_col     NUMERIC(10, 2),
                           real_col        REAL,
                           double_col      DOUBLE PRECISION,
                           money_col       MONEY,

                           -- Character types
                           char_col        CHAR(5),
                           varchar_col     VARCHAR(50),
                           text_col        TEXT,

                           -- Boolean
                           boolean_col     BOOLEAN,

                           -- Date & time
                           date_col        DATE,
                           time_col        TIME,
                           timetz_col      TIME WITH TIME ZONE,
                           timestamp_col   TIMESTAMP,
                           timestamptz_col TIMESTAMP WITH TIME ZONE,
                           interval_col INTERVAL,

                           -- JSON
                           json_col        JSON,
                           jsonb_col       JSONB,

                           -- Arrays
                           int_array_col   INTEGER[],
                           text_array_col  TEXT[],

                           -- Binary
                           bytea_col       BYTEA,

                           -- Enum
                           status_col      TEXT CHECK (status_col IN ('active', 'inactive', 'pending')),

                           -- Network
                           inet_col        INET,
                           cidr_col        CIDR,
                           macaddr_col     MACADDR,

                           -- Geometric
                           point_col       POINT,
                           circle_col      CIRCLE,

                           -- Bit string
                           bit_col         BIT(4),
                           bitvarying_col  BIT VARYING(8),

                           -- XML
                           xml_col         XML
                       );"""

    fill_table_sql = """
                     INSERT INTO all_types_demo (small_int_col,
                                                 int_col,
                                                 big_int_col,
                                                 numeric_col,
                                                 real_col,
                                                 double_col,
                                                 money_col,
                                                 char_col,
                                                 varchar_col,
                                                 text_col,
                                                 boolean_col,
                                                 date_col,
                                                 time_col,
                                                 timetz_col,
                                                 timestamp_col,
                                                 timestamptz_col,
                                                 interval_col,
                                                 json_col,
                                                 jsonb_col,
                                                 int_array_col,
                                                 text_array_col,
                                                 bytea_col,
                                                 status_col,
                                                 inet_col,
                                                 cidr_col,
                                                 macaddr_col,
                                                 point_col,
                                                 circle_col,
                                                 bit_col,
                                                 bitvarying_col,
                                                 xml_col)
                     VALUES (10,
                             1000,
                             10000000000,
                             12345.67,
                             3.14,
                             3.1415926535,
                             99.99,
                             'ABCDE',
                             'Hello PostgreSQL',
                             'This is a long text column',
                             TRUE,
                             '2025-01-01',
                             '12:30:00',
                             '12:30:00+02',
                             '2025-01-01 12:30:00',
                             '2025-01-01 12:30:00+02',
                             '2 days 3 hours',
                             '{"key": "value"}',
                             '{"key": "value"}',
                             ARRAY[1, 2, 3],
                             ARRAY['a', 'b', 'c'],
                             decode('DEADBEEF', 'hex'),
                             'active',
                             '192.168.1.1',
                             '192.168.0.0/24',
                             '08:00:2b:01:02:03',
                             POINT(1, 2),
                             CIRCLE(POINT(1, 2), 5),
                             B'1010',
                             B'101010',
                             '<root><child>value</child></root>');"""

    @classmethod
    def prepare_database(cls, container: PostgresContainer):
        host = container.get_container_host_ip()
        port = int(container.get_exposed_port(container.port))
        user = container.username
        password = container.password
        dbname = container.dbname

        conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=dbname)
        try:
            with conn.cursor() as cur:
                cur.execute(cls.create_table_sql)
                cur.execute(cls.fill_table_sql)
                conn.commit()
        finally:
            conn.close()

        return cls(
            datasource_name="my_postgres",
            host=host,
            port=port,
            database=dbname,
            user=user,
            password=password,
            check_connection=True,
        )
