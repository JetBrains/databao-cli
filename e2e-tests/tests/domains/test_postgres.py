from pathlib import Path

import allure
import pytest
from databases.postgres_utils import (
    CREATE_POSTGRES_PARTITIONED_TABLE_SQL,
    CREATE_POSTGRES_TABLE_SQL,
    FILL_POSTGRES_PARTITIONED_TABLE_SQL,
    FILL_POSTGRES_TABLE_SQL,
    PostgresDB,
)
from project_utils import execute_build, execute_init
from testcontainers.postgres import PostgresContainer
from utils.path_utils import get_datasource_result
from utils.yaml_compare import assert_introspections_equal


@pytest.fixture(scope="module")
def postgres_container():
    container = PostgresContainer("postgres:18.0", driver=None)
    container.start()
    try:
        yield container
    finally:
        container.stop()


@allure.title("Test databao build with Postgres")
@allure.description("Initialize a project with Postgres and build it, then compare results with expected introspection.")
def test_databao_build_postgres_with_various_table_types(project_folder: Path, postgres_container: PostgresContainer):
    db = PostgresDB.get_database(postgres_container)
    db.add_table(CREATE_POSTGRES_TABLE_SQL, FILL_POSTGRES_TABLE_SQL)
    execute_init(project_folder, db)
    execute_build(project_folder)
    assert_introspections_equal(get_datasource_result(project_folder, db.datasource_name), "postgres_introspections.yaml")


@allure.title("Test databao build with Postgres with partitioned table")
@allure.description("Initialize a project with Postgres with a partitioned table and build it.")
def test_databao_build_postgres_with_partitioned_table(project_folder: Path, postgres_container: PostgresContainer):
    db = PostgresDB.get_database(postgres_container)
    db.add_table(CREATE_POSTGRES_PARTITIONED_TABLE_SQL, FILL_POSTGRES_PARTITIONED_TABLE_SQL)
    db.add_table(CREATE_POSTGRES_TABLE_SQL, FILL_POSTGRES_TABLE_SQL)
    execute_init(project_folder, db)
    execute_build(project_folder)
    assert_introspections_equal(
        get_datasource_result(project_folder, db.datasource_name), "postgres_partitioned_tables_introspections.yaml"
    )
