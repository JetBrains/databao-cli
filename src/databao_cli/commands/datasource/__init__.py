import click


@click.group()
def datasource() -> None:
    """Manage datasource configurations."""


@datasource.command(name="add")
@click.option(
    "-d",
    "--domain",
    type=click.STRING,
    default="root",
    help="Databao domain name",
)
@click.pass_context
def add_datasource_config(ctx: click.Context, domain: str) -> None:
    """Add a new datasource configuration.

    The command will ask all relevant information for that datasource and save it in a chosen Databao domain
    """
    from databao_cli.commands._utils import get_project_or_exit
    from databao_cli.commands.datasource.add_datasource_config import add_datasource_config_interactive_impl

    project_layout = get_project_or_exit(ctx.obj["project_dir"])
    add_datasource_config_interactive_impl(project_layout, domain)


@datasource.command(name="check")
@click.argument(
    "domains",
    type=click.STRING,
    nargs=-1,
)
@click.pass_context
def check_datasource_config(ctx: click.Context, domains: tuple[str, ...]) -> None:
    """Check whether a datasource configuration is valid.

    The configuration is considered as valid if a connection with the datasource can be established.

    By default, all declared datasources across all domains in the project will be checked.
    You can explicitly list which domains to validate by using the [DOMAINS] argument.
    """
    from databao_cli.commands._utils import get_project_or_exit
    from databao_cli.commands.datasource.check_datasource_connection import check_datasource_connection_impl

    project_layout = get_project_or_exit(ctx.obj["project_dir"])
    check_datasource_connection_impl(project_layout, requested_domains=list(domains) if domains else None)
