from pathlib import Path

import click
from click import Command, Context

from databao_cli.commands.app import app
from databao_cli.commands.ask import ask
from databao_cli.commands.build import build
from databao_cli.commands.datasource import datasource
from databao_cli.commands.index import index
from databao_cli.commands.init import init
from databao_cli.commands.mcp import mcp
from databao_cli.commands.status import status
from databao_cli.commands.test import test
from databao_cli.shared.log.logging import configure_logging
from databao_cli.shared.project.layout import find_project

COMMANDS: list[Command] = [app, ask, build, datasource, index, init, mcp, status, test]


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Enable debug logging")
@click.option(
    "-p",
    "--project-dir",
    type=click.Path(file_okay=False, path_type=Path),
    help="Location of your Databao project",
)
@click.pass_context
def cli(ctx: Context, verbose: bool, project_dir: Path | None) -> None:
    """Databao Common CLI"""
    project_path = Path.cwd() if project_dir is None else project_dir.expanduser().resolve()

    ctx.ensure_object(dict)
    ctx.obj["project_dir"] = project_path

    configure_logging(find_project(project_path), verbose=verbose)


for command in COMMANDS:
    cli.add_command(command)


if __name__ == "__main__":
    cli()
