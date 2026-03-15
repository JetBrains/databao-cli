from pathlib import Path

import allure
import pytest
from databases.mysql_utils import CREATE_MYSQL_TABLE_SQL, FILL_MYSQL_TABLE_SQL, MysqlDB
from project_utils import execute_build, execute_init
from testcontainers.mysql import MySqlContainer
from utils.path_utils import get_datasource_result
from utils.yaml_compare import assert_introspections_equal


@pytest.fixture(scope="module")
def mysql_container():
    container = MySqlContainer()
    container.start()
    yield container
    container.stop()


@allure.title("Test databao build with MySQL")
@allure.description("Initialize a project with MySQL and build it, then compare results with expected introspection.")
def test_databao_build_mysql(project_folder: Path, mysql_container: MySqlContainer):
    db = MysqlDB.get_database(mysql_container)
    db.add_table(CREATE_MYSQL_TABLE_SQL, FILL_MYSQL_TABLE_SQL)
    execute_init(project_folder, db)
    execute_build(project_folder)
    assert_introspections_equal(get_datasource_result(project_folder, db.datasource_name), "mysql_introspections.yaml")
