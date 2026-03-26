from pathlib import Path

import allure
import pytest
from databases.sqlite_utils import CREATE_SQLITE_TABLE_SQL, FILL_SQLITE_TABLE_SQL, SqliteDB
from project_utils import execute_build, execute_init
from utils.path_utils import get_datasource_result
from utils.yaml_compare import assert_introspections_equal


@pytest.fixture
def temp_sqlite_file(tmp_path: Path):
    db_file = tmp_path / "test_db.sqlite"
    yield db_file


@allure.title("Test databao build with SQLite")
@allure.description("Initialize a project with SQLite and build it, then compare results with expected introspection.")
def test_databao_build_sqlite(project_folder: Path, temp_sqlite_file: Path):
    db = SqliteDB.get_database(temp_sqlite_file)
    db.add_table(CREATE_SQLITE_TABLE_SQL, FILL_SQLITE_TABLE_SQL)
    execute_init(project_folder, db)
    execute_build(project_folder)
    assert_introspections_equal(get_datasource_result(project_folder, db.datasource_name), "sqlite_introspections.yaml")
