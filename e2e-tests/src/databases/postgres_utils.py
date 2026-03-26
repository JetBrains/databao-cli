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

    @classmethod
    def get_database(cls, container: PostgresContainer):
        return cls(
            datasource_name="my_postgres",
            host=container.get_container_host_ip(),
            port=int(container.get_exposed_port(container.port)),
            database=container.dbname,
            user=container.username,
            password=container.password,
            check_connection=True,
        )

    def add_table(self, create_table_sql: str, fill_table_sql: str):
        conn = psycopg2.connect(host=self.host, port=self.port, user=self.user, password=self.password, dbname=self.database)
        try:
            with conn.cursor() as cur:
                cur.execute(create_table_sql)
                cur.execute(fill_table_sql)
                conn.commit()
        finally:
            conn.close()


CREATE_POSTGRES_TABLE_SQL = """
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

FILL_POSTGRES_TABLE_SQL = """
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

CREATE_POSTGRES_PARTITIONED_TABLE_SQL = """
                                        CREATE TABLE sales
                                        (
                                            id           SERIAL,
                                            sale_date    DATE NOT NULL,
                                            amount       NUMERIC(10, 2),
                                            product_name VARCHAR(100),
                                            region       VARCHAR(50)
                                        ) PARTITION BY RANGE (sale_date);

                                        CREATE TABLE sales_2024_q1 PARTITION OF sales
                                            FOR VALUES FROM
                                        (
                                            '2024-01-01'
                                        ) TO
                                        (
                                            '2024-04-01'
                                        );

                                        CREATE TABLE sales_2024_q2 PARTITION OF sales
                                            FOR VALUES FROM
                                        (
                                            '2024-04-01'
                                        ) TO
                                        (
                                            '2024-07-01'
                                        );

                                        CREATE TABLE sales_2024_q3 PARTITION OF sales
                                            FOR VALUES FROM
                                        (
                                            '2024-07-01'
                                        ) TO
                                        (
                                            '2024-10-01'
                                        );
                                        """

FILL_POSTGRES_PARTITIONED_TABLE_SQL = """
                                      INSERT INTO sales (sale_date, amount, product_name, region)
                                      VALUES ('2024-01-15', 150.00, 'Product A', 'North'),
                                             ('2024-05-20', 250.50, 'Product B', 'South'),
                                             ('2024-08-10', 175.75, 'Product C', 'East');
                                      """
