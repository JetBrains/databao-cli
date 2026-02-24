from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import yaml
from dotenv import load_dotenv
from pexpect import spawn
from pexpect.popen_spawn import PopenSpawn

from utils.path_utils import get_src_folder
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
class DatabaseBase:
    datasource_name: str

    @property
    def datasource_type(self) -> str:
        """Each DB subclass defines its own type."""
        raise NotImplementedError

    def run_interactive_flow(self, child: spawn | PopenSpawn) -> None:
        raise NotImplementedError("Must be implemented by subclasses")


@dataclass(frozen=True)
class SnowflakeDB(DatabaseBase):
    account: str
    warehouse: str | None = None
    database: str | None = None
    user: str | None = None
    role: str | None = None

    auth: SnowflakeAuth = SnowflakePasswordAuth()
    check_connection: bool = False

    @property
    def datasource_type(self) -> str:
        return "snowflake"

    def run_interactive_flow(self, child) -> None:
        """
        child: PopenSpawn(...)
        Executes the whole interactive flow for creating Snowflake datasource.
        """

        child_answer(child, r"What type of datasource do you want to add\?", self.datasource_type)
        child_answer(child, r"Datasource name\?:", self.datasource_name)
        (child_answer_safe(child, r"connection\.account\? :", self.account),)
        child_answer(child, r"connection\.warehouse\? \(Optional\):", self.warehouse)
        child_answer(child, r"connection\.database\? \(Optional\):", self.database)
        child_answer_safe(child, r"connection\.user\? \(Optional\):", self.user)
        child_answer(child, r"connection\.role\? \(Optional\):", self.role)
        self.auth.apply(child)
        child_answer(
            child,
            r"Do you want to check the connection to this new datasource\? \[y/N\]:",
            "y" if self.check_connection else "N",
        )
        child.expect(rf"{self.datasource_name}\.yaml\: Valid")


def create_snowflake_creds_file():
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
    get_src_folder(project_path).joinpath(name).write_text(
        yaml.safe_dump(create_snowflake_creds_file(), sort_keys=False, indent=2)
    )
