from pathlib import Path

import allure
import pexpect
from databases.bigquery_utils import BigQueryDB
from databases.duckdb_utils import DuckdbDB
from databases.mysql_utils import MysqlDB
from databases.postgres_utils import PostgresDB
from databases.snowflake_utils import SnowflakeDB
from databases.sqlite_utils import SqliteDB
from pexpect import spawn
from pexpect.popen_spawn import PopenSpawn
from utils.pexpect_utils import child_answer, child_answer_safe


@allure.step("Executing databao init")
def execute_init(project_dir: Path, db: PostgresDB | MysqlDB | SnowflakeDB | BigQueryDB | None = None):
    log_file_path = project_dir / "cli.log"
    with open(log_file_path, "w") as logfile:
        try:
            # Use PopenSpawn for debugging
            child = pexpect.spawn("uv run databao init", cwd=project_dir, encoding="utf-8", timeout=30, logfile=logfile)

            child.expect(r"Do you want to configure a domain now\? \[y/N\]:")
            if db:
                child.sendline("Y")
                run_common_interactive_flow(child, db)
            else:
                child.sendline("N")
                child.expect(pexpect.EOF)
        finally:
            if log_file_path.exists():
                allure.attach.file(log_file_path, name="cli.log", attachment_type=allure.attachment_type.TEXT)


@allure.step("Executing databao build")
def execute_build(project_dir: Path):
    log_file_path = project_dir / "cli.log"
    with open(log_file_path, "w") as logfile:
        child = pexpect.spawn("uv run databao build", cwd=project_dir, encoding="utf-8", timeout=900, logfile=logfile)
        try:
            # Wait for Ollama download/installation with extended timeout
            if child.expect([
                r"Ollama model .+ not found locally\.",
                r"No existing Ollama installation detected",
                r"We will download and install Ollama.",
                r"Downloading .*ollama.*\.tgz",
                r"Found datasource of type",
            ], timeout=5) == 0:
                with allure.step("Ollama model not found locally, installing..."):
                    child.expect("Ollama model .+ pulled successfully", timeout=900)
            child.expect(r"Build complete\. Processed \d+ datasources\.", timeout=30)
            child.expect(pexpect.EOF)
        finally:
            if log_file_path.exists():
                allure.attach.file(log_file_path, name="cli.log", attachment_type=allure.attachment_type.TEXT)


@allure.step("Interactive domain configuration")
def run_common_interactive_flow(
    child: spawn | PopenSpawn, database: PostgresDB | SnowflakeDB | MysqlDB | SqliteDB | DuckdbDB
) -> None:
    child_answer(child, r"What type of datasource do you want to add\?", database.datasource_type)
    child_answer(child, r"Datasource name\?:", database.datasource_name)

    if isinstance(database, SnowflakeDB):
        (child_answer_safe(child, r"connection\.account\?:", database.account),)
        child_answer(child, r"connection\.warehouse\? \(Optional\):", database.warehouse)
        child_answer(child, r"connection\.database\? \(Optional\):", database.database)
        child_answer_safe(child, r"connection\.user\? \(Optional\):", database.user)
        child_answer(child, r"connection\.role\? \(Optional\):", database.role)
        database.auth.apply(child)
    elif isinstance(database, BigQueryDB):
        (child_answer_safe(child, r"connection\.project?\?:", database.project),)
        child_answer_safe(child, r"connection\.dataset\? \(Optional\):", database.dataset)
        child_answer_safe(child, r"connection\.location\? \(Optional\):", database.location)
        database.auth.apply(child)
    elif isinstance(database, (SqliteDB, DuckdbDB)):
        child_answer_safe(child, r"connection\.database_path\?:", database.database_path)
    else:
        child_answer(child, r"connection\.host\? \[localhost\]:", database.host)
        child_answer(child, r"connection\.port\? \(Optional\):", database.port)
        child_answer(child, r"connection\.database\? \(Optional\):", database.database)
        child_answer(child, r"connection\.user\? \(Optional\):", database.user)
        child_answer_safe(child, r"connection\.password\? \(Optional\):", database.password)

    child_answer(
        child,
        r"Do you want to check the connection to this new datasource\? \[y/N\]:",
        "y" if database.check_connection else "N",
    )
    if database.check_connection:
        if database.check_connection_succeed:
            child.expect(rf"{database.datasource_name}\.yaml\: Valid")
        else:
            child.expect(rf"{database.datasource_name}\.yaml\: Invalid")
    child.expect(r"Do you want to add more datasources\? \[y/N\]:")
    child.sendline("N")
    child.expect(pexpect.EOF)
