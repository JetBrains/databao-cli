import click

from databao_cli.shared.cli_utils import handle_feature_errors


@click.command()
@click.pass_context
@handle_feature_errors
def status(ctx: click.Context) -> None:
    """Display project status and system-wide information."""
    from databao_cli.features.status import status_impl

    click.echo(status_impl(ctx.obj["project_dir"]))
