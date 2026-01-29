from pathlib import Path

import click
from click import Context

from databao.agents.hello import agents
from databao.commands.status import echo_status


@click.group()
@click.option(
    "-d",
    "--project-dir",
    type=click.Path(file_okay=False),
    help="Location of your Databao Context Engine project",
)
@click.pass_context
def cli(ctx: Context, project_dir: Path | None):
    """Databao Common CLI"""
    if project_dir is None:
        project_path = Path.cwd()
    else:
        project_path = Path(project_dir.name).expanduser()

    ctx.ensure_object(dict)
    ctx.obj["project_dir"] = project_path


@cli.command()
@click.pass_context
def status(ctx: Context) -> None:
    """Display project status and system-wide information."""
    echo_status(ctx.obj["project_dir"])


cli.add_command(agents)

if __name__ == "__main__":
    cli()
