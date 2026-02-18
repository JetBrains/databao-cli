import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from click.testing import CliRunner, Result

from databao_cli.__main__ import cli


@contextmanager
def run_init(run_dir: Path, args: list[str] | None = None, answers: list[str] | None = None) -> Iterator[Result]:
    if args is None:
        args = ["init"]
    if answers is None:
        answers = ["N"]
    with run_databao_cmd(run_dir=run_dir, args=args, answers=answers) as result:
        yield result


@contextmanager
def run_build(run_dir: Path, args: list[str] | None = None, answers: list[str] | None = None) -> Iterator[Result]:
    if args is None:
        args = ["build"]
    with run_databao_cmd(run_dir=run_dir, args=args, answers=answers) as result:
        yield result


@contextmanager
def run_databao_cmd(run_dir: Path, args: list[str] | None = None, answers: list[str] | None = None) -> Iterator[Result]:
    runner = CliRunner()
    inputs = os.linesep.join(answers) if answers else ""
    with within_dir(run_dir):
        yield runner.invoke(cli=cli, args=args, input=inputs, catch_exceptions=False)


def describe_result(result: Result) -> str:
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
