import os
from dataclasses import dataclass

from dotenv import load_dotenv
from utils.pexpect_utils import child_answer, child_answer_safe

load_dotenv()

BQ_PROJECT_HIDDEN = """{{ env_var("BQ_PROJECT") }}"""
BQ_DATASET_HIDDEN = """{{ env_var("BQ_DATASET") }}"""
BQ_SERVICE_ACCOUNT_JSON_HIDDEN = """{{ env_var("BQ_SERVICE_ACCOUNT_JSON") }}"""
BQ_SERVICE_ACCOUNT_JSON = os.getenv("BQ_SERVICE_ACCOUNT_JSON")


@dataclass(frozen=True)
class BigQueryDefaultAuth:
    @staticmethod
    def apply(child) -> None:
        child_answer(child, r"connection\.auth\.type\?", "BigQueryDefaultAuth")


@dataclass(frozen=True)
class BigQueryServiceAccountKeyFileAuth:
    credentials_file: str | None = None

    def apply(self, child) -> None:
        child_answer(child, r"connection\.auth\.type\?", "BigQueryServiceAccountKeyFileAuth")
        child_answer_safe(child, r"connection\.auth\.credentials_file\?:", self.credentials_file)


@dataclass(frozen=True)
class BigQueryServiceAccountJsonAuth:
    credentials_json: str | None = None

    def apply(self, child) -> None:
        child_answer(child, r"connection\.auth\.type\?", "BigQueryServiceAccountJsonAuth")
        child_answer_safe(child, r"connection\.auth\.credentials_json\? \(Optional\)", self.credentials_json)


@dataclass()
class BigQueryDB:
    datasource_name = "my_test_bigquery"
    datasource_type = "bigquery"
    project: str
    dataset: str | None = None
    location: str | None = None
    auth: BigQueryDefaultAuth | BigQueryServiceAccountKeyFileAuth | BigQueryServiceAccountJsonAuth = BigQueryDefaultAuth()
    check_connection: bool = False
    check_connection_succeed: bool = True
