from pathlib import Path

import pexpect
from databases.mysql_utils import MysqlDB
from databases.postgres_utils import PostgresDB
from databases.snowflake_utils import SnowflakeDB
from databases.sqlite_utils import SqliteDB
from pexpect import spawn
from pexpect.popen_spawn import PopenSpawn
from utils.pexpect_utils import child_answer, child_answer_safe


def execute_init(project_dir: Path, db: PostgresDB | MysqlDB | SnowflakeDB | None = None):
    with open(project_dir / "cli.log", "w") as logfile:
        # child = PopenSpawn(
        child = pexpect.spawn("uv run databao init", cwd=project_dir, encoding="utf-8", timeout=30, logfile=logfile)

        child.expect(r"Do you want to configure a domain now\? \[y/N\]:")
        if db:
            child.sendline("Y")
            run_common_interactive_flow(child, db)
        else:
            child.sendline("N")
            child.expect(pexpect.EOF)


def execute_build(project_dir: Path):
    with open(project_dir / "cli.log", "w") as logfile:
        # child = PopenSpawn(
        child = pexpect.spawn("uv run databao build", cwd=project_dir, encoding="utf-8", timeout=140, logfile=logfile)
        child.expect("Found datasource of type")
        child.expect(pexpect.EOF)


def run_common_interactive_flow(child: spawn | PopenSpawn,
                                database: PostgresDB | SnowflakeDB | MysqlDB | SqliteDB) -> None:
    child_answer(child, r"What type of datasource do you want to add\?", database.datasource_type)
    child_answer(child, r"Datasource name\?:", database.datasource_name)

    if type(database) is SnowflakeDB:
        (child_answer_safe(child, r"connection\.account\? :", database.account),)
        child_answer(child, r"connection\.warehouse\? \(Optional\):", database.warehouse)
        child_answer(child, r"connection\.database\? \(Optional\):", database.database)
        child_answer_safe(child, r"connection\.user\? \(Optional\):", database.user)
        child_answer(child, r"connection\.role\? \(Optional\):", database.role)
        database.auth.apply(child)
    elif type(database) is SqliteDB:
        (child_answer_safe(child, r"connection\.database_path\? :", database.database_path))
    else:
        child_answer(child, r"connection\.host\?  \[localhost\]:", database.host)
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
