from pathlib import Path

import pytest
from databases.mysql_utils import MysqlDB
from project_utils import execute_build, execute_init
from testcontainers.mysql import MySqlContainer
from utils.path_utils import get_all_results
from utils.yaml_compare import assert_introspections_equal


@pytest.fixture(scope="module")
def mysql_container():
    container = MySqlContainer()
    container.start()
    yield container
    container.stop()


def test_databao_build_mysql(project_folder: Path, mysql_container: MySqlContainer):
    db = MysqlDB.prepare_database(mysql_container)
    execute_init(project_folder, db)
    execute_build(project_folder)
    assert_introspections_equal(get_all_results(project_folder), "mysql_introspections.yaml")
