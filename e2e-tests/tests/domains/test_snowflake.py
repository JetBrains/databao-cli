from pathlib import Path

from databases.snowflake_utils import (
    SN_ACCOUNT,
    SN_PASSWORD,
    SN_USER,
    SnowflakeDB,
    SnowflakePasswordAuth,
    create_and_save_snowflake_creds_file,
    create_snowflake_creds_file,
)
from project_utils import execute_build, execute_init
from utils.path_utils import get_all_results, get_src_folder
from utils.yaml_compare import assert_introspections_equal, compare_yaml, load_yaml


def test_databao_build_snowflake_datasource(project_folder: Path):
    con_filename = "sn_con.yaml"
    execute_init(project_folder)
    create_and_save_snowflake_creds_file(project_folder, con_filename)
    execute_build(project_folder)
    assert_introspections_equal(get_all_results(project_folder), "snowflake_introspections.yaml")


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

    expected_config = create_snowflake_creds_file()
    expected_config["connection"].pop("schema", None)  # not supported yet

    compare_yaml(load_yaml(get_src_folder(project_folder) / f"{con_filename}.yaml"), expected_config)
