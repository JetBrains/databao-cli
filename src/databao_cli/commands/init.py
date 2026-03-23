import sys
from pathlib import Path

import click

from databao_cli.features.init.errors import InitDatabaoProjectError, ProjectDirDoesnotExistError
from databao_cli.features.init.service import init_impl
from databao_cli.shared.cli_utils import handle_feature_errors
from databao_cli.shared.project.layout import ROOT_DOMAIN, ProjectLayout


@click.command()
@click.pass_context
@handle_feature_errors
def init(ctx: click.Context) -> None:
    """Create a new Databao project."""
    from databao_cli.workflows.datasource.add import add_workflow as add_datasource_config_interactive_impl

    project_dir: Path = ctx.obj["project_dir"]
    project_layout: ProjectLayout
    try:
        project_layout = init_impl(project_dir)
    except ProjectDirDoesnotExistError:
        if click.confirm(
            f"The directory {project_dir.resolve()} does not exist. Do you want to create it?",
            default=True,
        ):
            project_dir.mkdir(parents=True, exist_ok=False)
            project_layout = init_impl(project_dir)
        else:
            return
    except InitDatabaoProjectError as e:
        click.echo(e.message, err=True)
        sys.exit(1)

    click.echo(f"Project initialized successfully at {project_dir.resolve()}")

    if not click.confirm("\nDo you want to configure a domain now?"):
        return

    add_datasource_config_interactive_impl(project_layout, ROOT_DOMAIN)

    while click.confirm("\nDo you want to add more datasources?"):
        add_datasource_config_interactive_impl(project_layout, ROOT_DOMAIN)
