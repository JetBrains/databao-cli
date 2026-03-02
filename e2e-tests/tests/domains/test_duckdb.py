from pathlib import Path

import pytest
from databases.duckdb_utils import DuckdbDB
from project_utils import execute_build, execute_init
from utils.path_utils import get_all_results
from utils.yaml_compare import assert_introspections_equal


@pytest.fixture
def temp_duckdb_file(tmp_path: Path):
    db_file = tmp_path / "test_db.duckdb"
    yield db_file


def test_databao_build_duckdb(project_folder: Path, temp_duckdb_file: Path):
    db = DuckdbDB.prepare_database(temp_duckdb_file)
    execute_init(project_folder, db)
    execute_build(project_folder)
    assert_introspections_equal(get_all_results(project_folder), "duckdb_introspections.yaml")
