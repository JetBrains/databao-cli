import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import yaml
from click.testing import CliRunner, Result

from databao_cli.__main__ import cli


def test_databao_init_successfully(tmp_path: Path):
    with run_init(tmp_path) as result:
        assert result.exit_code == 0, desribe_result(result)
        assert_created_project_is_valid(tmp_path)


def test_databao_project_already_exists(tmp_path: Path):
    (Path(tmp_path) / "databao").mkdir()
    with run_init(tmp_path) as result:
        assert result.exit_code == 1, desribe_result(result)
        assert "Can't initialize Databao project. It already exists" in result.stderr, result.stderr


def test_databao_project_already_exists_in_parent_dir(tmp_path: Path):
    subdirectory = tmp_path / "subdirectory"
    subdirectory.mkdir()
    (Path(tmp_path) / "databao").mkdir()

    with run_init(tmp_path) as result:
        assert result.exit_code == 1, desribe_result(result)
        assert "Can't initialize Databao project. It already exists" in result.stderr, result.stderr


def test_init_with_project_dir_argument(tmp_path: Path):
    inputs = os.linesep.join(["N"])
    result = CliRunner().invoke(cli=cli, args=["-p", str(tmp_path), "init"], input=inputs, catch_exceptions=False)
    assert result.exit_code == 0, desribe_result(result)
    assert_created_project_is_valid(tmp_path)


def test_init_project_with_snowflake(tmp_path: Path):
    answers = [
        "Y",
        "snowflake",
        "my_test_snow",
        "test_connection_acc",
        "test_warehouse",
        "test_db",
        "test_user",
        "test_role",
        "SnowflakeKeyPairAuth",
        "my_private_key_file",
        "my_private_key_password",
        "my_private_key",
        # dont check connection to this datasource
        "N",
    ]
    with run_init(tmp_path, answers=answers) as result:
        assert result.exit_code == 0, desribe_result(result)
        created_snowflake_config = "databao/domains/root/src/my_test_snow.yaml"
        assert_created_project_is_valid(tmp_path, additional_expected_files=[created_snowflake_config])
        assert yaml.safe_load((tmp_path / created_snowflake_config).read_text()) == {
            "type": "snowflake",
            "name": "my_test_snow",
            "connection": {
                "account": "test_connection_acc",
                "warehouse": "test_warehouse",
                "database": "test_db",
                "user": "test_user",
                "role": "test_role",
                "auth": {
                    "private_key_file": "my_private_key_file",
                    "private_key_file_pwd": "my_private_key_password",
                    "private_key": "my_private_key",
                },
            },
        }


def assert_created_project_is_valid(project_dir: Path | str, additional_expected_files: list[str] = None) -> None:
    expected_directories = {
        "databao/agents",
        "databao/domains/root/src",
    }
    expected_files = {
        "databao/domains/root/dce.ini",
    }
    if additional_expected_files:
        expected_files.union(set(additional_expected_files))
    for dirpath, dirnames, filenames in os.walk(project_dir):
        for dirname in dirnames:
            absolute_dir = Path(dirpath) / dirname
            relative_dir = str(absolute_dir.relative_to(project_dir))
            if relative_dir in expected_directories:
                expected_directories.remove(relative_dir)

        for filename in filenames:
            absolute_file = Path(dirpath) / filename
            relative_file = str(absolute_file.relative_to(project_dir))
            if relative_file in expected_files:
                expected_files.remove(str(relative_file))

    assert len(expected_directories) == 0, expected_directories
    assert len(expected_files) == 0, expected_files


@contextmanager
def run_init(run_dir: Path, args: list[str] = None, answers: list[str] = None) -> Iterator[Result]:
    if args is None:
        args = ["init"]
    runner = CliRunner()
    if answers is None:
        answers = ["N"]
    inputs = os.linesep.join(answers)
    with within_dir(run_dir):
        yield runner.invoke(cli=cli, args=args, input=inputs, catch_exceptions=False)


def desribe_result(result: Result) -> str:
    return f"""
    stdout: {result.stdout}
    stderr: {result.stderr}
"""


@contextmanager
def within_dir(dir: Path) -> Iterator[Path]:
    cwd = os.getcwd()
    os.chdir(dir)
    try:
        yield dir
    finally:
        os.chdir(cwd)
