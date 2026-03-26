import click

from databao_cli.shared.cli_utils import get_project_or_raise, handle_feature_errors


@click.command(name="add")
@click.option(
    "-d",
    "--domain",
    type=click.STRING,
    default="root",
    help="Databao domain name",
)
@click.pass_context
@handle_feature_errors
def add(ctx: click.Context, domain: str) -> None:
    """Add a new datasource configuration.

    The command will ask all relevant information for that datasource and save it in a chosen Databao domain
    """
    from databao_cli.workflows.datasource.add import add_workflow

    project_layout = get_project_or_raise(ctx.obj["project_dir"])
    add_workflow(project_layout, domain)
