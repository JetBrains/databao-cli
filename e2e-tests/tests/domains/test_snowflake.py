import os
from pathlib import Path

import allure
import pytest
from databases.snowflake_utils import get_working_snowflake_connection
from project_utils import execute_build, execute_init
from utils.path_utils import get_datasource_result
from utils.yaml_compare import assert_introspections_equal

_snowflake_credentials_available = bool(os.getenv("SNOWFLAKE_ACCOUNT"))
_skip_reason = "Snowflake credentials not available (SNOWFLAKE_ACCOUNT not set)"


@pytest.mark.skipif(not _snowflake_credentials_available, reason=_skip_reason)
@allure.title("Test databao build with Snowflake from init config")
@allure.description(
    "Initialize a project with Snowflake using interactive configuration and verify the generated config file."
)
def test_databao_build_snowflake_datasource_from_init_config(project_folder: Path):
    db = get_working_snowflake_connection()
    execute_init(project_folder, db)
    execute_build(project_folder)
    assert_introspections_equal(get_datasource_result(project_folder, db.datasource_name), "snowflake_introspections.yaml")
