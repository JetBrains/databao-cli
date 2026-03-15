from pathlib import Path

import allure
from databases.snowflake_utils import get_working_snowflake_connection
from project_utils import execute_build, execute_init
from utils.path_utils import get_datasource_result
from utils.yaml_compare import assert_introspections_equal


@allure.title("Test databao build with Snowflake from init config")
@allure.description(
    "Initialize a project with Snowflake using interactive configuration and verify the generated config file."
)
def test_databao_build_snowflake_datasource_from_init_config(project_folder: Path):
    db = get_working_snowflake_connection()
    execute_init(project_folder, db)
    execute_build(project_folder)
    assert_introspections_equal(get_datasource_result(project_folder, db.datasource_name), "snowflake_introspections.yaml")
