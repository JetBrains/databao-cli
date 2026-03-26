import click

from databao_cli.shared.cli_utils import handle_feature_errors


@click.command()
@click.option(
    "-d",
    "--domain",
    type=click.STRING,
    default="root",
    help="Databao domain name",
)
@click.argument(
    "datasources-config-files",
    nargs=-1,
    type=click.STRING,
)
@click.pass_context
@handle_feature_errors
def index(ctx: click.Context, domain: str, datasources_config_files: tuple[str, ...]) -> None:
    """Index built contexts into the embeddings database.

    If one or more datasource config file strings are provided, only those datasources will be indexed.
    If no values are provided, all built contexts for the selected domain will be indexed.
    """
    from databao_cli.features.index import index_impl
    from databao_cli.shared.cli_utils import get_project_or_raise

    project_layout = get_project_or_raise(ctx.obj["project_dir"])
    datasources = list(datasources_config_files) if datasources_config_files else None
    results = index_impl(project_layout, domain, datasources)
    click.echo(f"Index complete. Processed {len(results)} contexts.")
