from pathlib import Path

import allure
from databases.snowflake_utils import (
    SN_ACCOUNT,
    SN_PASSWORD,
    SN_USER,
    SnowflakeDB,
    SnowflakePasswordAuth,
)
from project_utils import execute_build, execute_init
from utils.path_utils import get_all_results
from utils.yaml_compare import assert_introspections_equal


@allure.title("Test databao build with Snowflake from init config")
@allure.description(
    "Initialize a project with Snowflake using interactive configuration and verify the generated config file."
)
def test_databao_build_snowflake_datasource_from_init_config(project_folder: Path):
    con_filename = "my_test_snowflake"
    db = SnowflakeDB(
        datasource_name=con_filename,
        account=SN_ACCOUNT,
        warehouse="DEMO_WH",
        database="DATALORE",
        user=SN_USER,
        auth=SnowflakePasswordAuth(password=SN_PASSWORD),
        check_connection=True,
    )
    execute_init(project_folder, db)
    execute_build(project_folder)
    assert_introspections_equal(get_all_results(project_folder), "snowflake_introspections.yaml")
