from dataclasses import dataclass

from dotenv import load_dotenv
from utils.pexpect_utils import child_answer, child_answer_safe

load_dotenv()


@dataclass(frozen=True)
class SnowflakePasswordAuth:
    password: str | None = None

    def apply(self, child) -> None:
        child_answer(child, r"connection\.auth\.type\?", "SnowflakePasswordAuth")
        child_answer_safe(child, r"connection\.auth\.password\? \(Optional\):", self.password)


@dataclass(frozen=True)
class SnowflakeKeyPairAuth:
    private_key_file: str | None = None
    private_key_file_pwd: str | None = None
    private_key: str | None = None

    def apply(self, child) -> None:
        child_answer(child, r"connection\.auth\.type\?", "SnowflakeKeyPairAuth")
        child_answer_safe(child, r"connection\.auth\.private_key_file\? \(Optional\):", self.private_key_file)
        child_answer_safe(child, r"connection\.auth\.private_key_file_pwd\? \(Optional\):", self.private_key_file_pwd)
        child_answer_safe(child, r"connection\.auth\.private_key\? \(Optional\):", self.private_key)


@dataclass(frozen=True)
class SnowflakeSSOAuth:
    authenticator: str | None = None

    def apply(self, child) -> None:
        child_answer(child, r"connection\.auth\.type\?", "SnowflakeKeyPairAuth")
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


def get_working_snowflake_connection() -> SnowflakeDB:
    return SnowflakeDB(
        datasource_name="my_test_snowflake",
        account="""{{ env_var("SNOWFLAKE_ACCOUNT") }}""",
        warehouse="""{{ env_var("SNOWFLAKE_WAREHOUSE") }}""",
        database="""{{ env_var("SNOWFLAKE_DATABASE") }}""",
        user="""{{ env_var("SNOWFLAKE_TEST_USER") }}""",
        auth=SnowflakeKeyPairAuth(private_key="""{{ env_var("SNOWFLAKE_PRIVATE_TOKEN") }}"""),
        check_connection=True,
    )
