from pathlib import Path

import allure
from databases.bigquery_utils import (
    BQ_DATASET_HIDDEN,
    BQ_PROJECT_HIDDEN,
    BQ_SERVICE_ACCOUNT_JSON,
    BQ_SERVICE_ACCOUNT_JSON_HIDDEN,
    BigQueryDB,
    BigQueryServiceAccountJsonAuth,
    BigQueryServiceAccountKeyFileAuth,
)
from project_utils import execute_build, execute_init
from utils.path_utils import get_datasource_result
from utils.yaml_compare import assert_introspections_equal


@allure.title("Test databao build with BigQuery using BigQueryServiceAccountJsonAuth auth type")
@allure.description("Initialize a project with BigQuery and build it, then compare results with expected introspection.")
def test_databao_build_bigquery_datasource_from_init_config_from_json(project_folder: Path, tmp_path: Path):
    db = BigQueryDB(
        project=BQ_PROJECT_HIDDEN,
        dataset=BQ_DATASET_HIDDEN,
        auth=BigQueryServiceAccountJsonAuth(credentials_json=BQ_SERVICE_ACCOUNT_JSON_HIDDEN),
        check_connection=True,
    )
    execute_init(project_folder, db)
    execute_build(project_folder)
    assert_introspections_equal(get_datasource_result(project_folder, db.datasource_name), "bigquery_introspections.yaml")


@allure.title("Test databao build with BigQuery using BigQueryServiceAccountKeyFileAuth auth type")
@allure.description("Initialize a project with BigQuery and build it, then compare results with expected introspection.")
def test_databao_build_bigquery_datasource_from_init_config_from_json_file_path(project_folder: Path, tmp_path: Path):
    service_account_file_path = tmp_path / "service_account.json"
    service_account_file_path.write_text(BQ_SERVICE_ACCOUNT_JSON)

    db = BigQueryDB(
        project=BQ_PROJECT_HIDDEN,
        dataset=BQ_DATASET_HIDDEN,
        auth=BigQueryServiceAccountKeyFileAuth(credentials_file=str(service_account_file_path)),
        check_connection=True,
    )
    execute_init(project_folder, db)
    execute_build(project_folder)
    assert_introspections_equal(get_datasource_result(project_folder, db.datasource_name), "bigquery_introspections.yaml")
