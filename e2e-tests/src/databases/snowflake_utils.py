from asyncio import Protocol
from dataclasses import dataclass
from pathlib import Path

from databases.database_utils import create_and_save_database_creds_file
from dotenv import load_dotenv
from utils.pexpect_utils import child_answer, child_answer_safe

load_dotenv()

SN_ACCOUNT = """{{ env_var("SNOWFLAKE_ACCOUNT") }}"""
SN_USER = """{{ env_var("SNOWFLAKE_TEST_USER") }}"""
SN_PASSWORD = """{{ env_var("SNOWFLAKE_TEST_USER_PROGRAM_TOKEN") }}"""


class SnowflakeAuth(Protocol):
    def auth_type_name(self) -> str: ...

    def apply(self, child) -> None: ...


@dataclass(frozen=True)
class SnowflakePasswordAuth:
    password: str | None = None

    def auth_type_name(self) -> str:
        return "SnowflakePasswordAuth"

    def apply(self, child) -> None:
        child_answer(child, r"connection\.auth\.type\?", self.auth_type_name())
        child_answer_safe(child, r"connection\.auth\.password\? \(Optional\):", self.password)


@dataclass(frozen=True)
class SnowflakeKeyPairAuth:
    private_key_file: str | None = None
    private_key_file_pwd: str | None = None
    private_key: str | None = None

    def auth_type_name(self) -> str:
        return "SnowflakeKeyPairAuth"

    def apply(self, child) -> None:
        child_answer(child, r"connection\.auth\.type\?", self.auth_type_name())
        child_answer_safe(child, r"connection\.auth\.private_key_file\? \(Optional\) :", self.private_key_file)
        child_answer_safe(child, r"connection\.auth\.private_key_file_pwd\? \(Optional\) :", self.private_key_file_pwd)
        child_answer_safe(child, r"connection\.auth\.private_key\? \(Optional\) :", self.private_key)


@dataclass(frozen=True)
class SnowflakeSSOAuth:
    authenticator: str | None = None

    def auth_type_name(self) -> str:
        return "SnowflakeSSOAuth"

    def apply(self, child) -> None:
        child_answer(child, r"connection\.auth\.type\?", self.auth_type_name())
        child_answer_safe(child, r"connection\.auth\.authenticator\? \(Optional\) :", self.authenticator)


@dataclass(frozen=True)
class SnowflakeDB:
    datasource_name: str
    datasource_type = "snowflake"
    account: str
    warehouse: str | None = None
    database: str | None = None
    user: str | None = None
    role: str | None = None
    auth: SnowflakePasswordAuth | SnowflakeKeyPairAuth | SnowflakeSSOAuth = SnowflakePasswordAuth()
    check_connection: bool = False
    check_connection_succeed: bool = True


def create_snowflake_creds_file() -> dict[str, str | None]:
    return {
        "type": "snowflake",
        "name": "my_test_snowflake",
        "connection": {
            "account": SN_ACCOUNT,
            "warehouse": "DEMO_WH",
            "database": "DATALORE",
            "schema": "TEST",
            "user": SN_USER,
            "auth": {
                "password": SN_PASSWORD,
            },
        },
    }


def create_and_save_snowflake_creds_file(project_path: Path, name: str):
    create_and_save_database_creds_file(project_path, name, create_snowflake_creds_file())
