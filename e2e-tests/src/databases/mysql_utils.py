from dataclasses import dataclass

import pymysql
from testcontainers.mysql import MySqlContainer


@dataclass(frozen=True)
class MysqlDB:
    datasource_name: str | None = "test_mysql_conn"
    datasource_type: str = "mysql"
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
                           id             INT AUTO_INCREMENT PRIMARY KEY,
                           tinyint_col    TINYINT,
                           smallint_col   SMALLINT,
                           mediumint_col  MEDIUMINT,
                           int_col        INT,
                           bigint_col     BIGINT,
                           decimal_col    DECIMAL(10, 2),
                           float_col      FLOAT,
                           double_col DOUBLE,
                           bit_col        BIT(4),
                           boolean_col    BOOLEAN,

                           -- Date and time types
                           date_col       DATE,
                           time_col       TIME,
                           datetime_col   DATETIME,
                           timestamp_col  TIMESTAMP NULL,
                           year_col YEAR,

                           -- String types
                           char_col       CHAR(5),
                           varchar_col    VARCHAR(50),
                           binary_col     BINARY(4),
                           varbinary_col  VARBINARY(10),

                           -- Text types
                           tinytext_col   TINYTEXT,
                           text_col       TEXT,
                           mediumtext_col MEDIUMTEXT,
                           longtext_col   LONGTEXT,

                           -- Blob types
                           tinyblob_col   TINYBLOB,
                           blob_col       BLOB,
                           mediumblob_col MEDIUMBLOB,
                           longblob_col   LONGBLOB,

                           -- Enum and Set
                           enum_col       ENUM('active','inactive','pending'),
                           set_col SET('a','b','c'),

                           -- JSON
                           json_col       JSON,

                           -- Spatial types
                           point_col      POINT,
                           linestring_col LINESTRING,
                           polygon_col    POLYGON
                       );"""

    fill_table_sql = """
                     INSERT INTO all_types_demo (tinyint_col,
                                                 smallint_col,
                                                 mediumint_col,
                                                 int_col,
                                                 bigint_col,
                                                 decimal_col,
                                                 float_col,
                                                 double_col,
                                                 bit_col,
                                                 boolean_col,
                                                 date_col,
                                                 time_col,
                                                 datetime_col,
                                                 timestamp_col,
                                                 year_col,
                                                 char_col,
                                                 varchar_col,
                                                 binary_col,
                                                 varbinary_col,
                                                 tinytext_col,
                                                 text_col,
                                                 mediumtext_col,
                                                 longtext_col,
                                                 tinyblob_col,
                                                 blob_col,
                                                 mediumblob_col,
                                                 longblob_col,
                                                 enum_col,
                                                 set_col,
                                                 json_col,
                                                 point_col,
                                                 linestring_col,
                                                 polygon_col)
                     VALUES (1,
                             100,
                             1000,
                             10000,
                             10000000000,
                             12345.67,
                             3.14,
                             3.1415926535,
                             b'1010',
                             TRUE,
                             '2025-01-01',
                             '12:30:00',
                             '2025-01-01 12:30:00',
                             '2026-02-26 15:12:55',
                             2025,
                             'ABCDE',
                             'Hello MySQL',
                             'ABCD',
                             'varbin',
                             'tiny text',
                             'regular text column',
                             'medium text column',
                             'long text column',
                             UNHEX('AA'),
                             UNHEX('DEADBEEF'),
                             UNHEX('DEADBEEFDEADBEEF'),
                             UNHEX('DEADBEEFDEADBEEFDEADBEEF'),
                             'active',
                             'a,b',
                             JSON_OBJECT('key', 'value'),
                             ST_GeomFromText('POINT(1 2)'),
                             ST_GeomFromText('LINESTRING(0 0, 1 1, 2 2)'),
                             ST_GeomFromText('POLYGON((0 0, 0 5, 5 5, 5 0, 0 0))'));"""

    @classmethod
    def prepare_database(cls, container: MySqlContainer):
        host = container.get_container_host_ip()
        port = int(container.get_exposed_port(container.port))
        user = container.username
        password = container.password
        dbname = container.dbname

        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=dbname,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )
        try:
            with conn.cursor() as cur:
                cur.execute(cls.create_table_sql)
                cur.execute(cls.fill_table_sql)
        finally:
            conn.close()

        return cls(host=host, port=port, database=dbname, user=user, password=password, check_connection=True)
