from pathlib import Path

import pytest
from databases.postgres_utils import PostgresDB
from project_utils import execute_build, execute_init
from testcontainers.postgres import PostgresContainer
from utils.path_utils import get_all_results
from utils.yaml_compare import assert_introspections_equal


@pytest.fixture(scope="module")
def postgres_container():
    container = PostgresContainer("postgres:18.0", driver=None)
    container.start()
    try:
        yield container
    finally:
        container.stop()


def test_databao_build_postgres(project_folder: Path, postgres_container: PostgresContainer):
    db = PostgresDB.prepare_database(postgres_container)
    execute_init(project_folder, db)
    execute_build(project_folder)
    assert_introspections_equal(get_all_results(project_folder), "postgres_introspections.yaml")
